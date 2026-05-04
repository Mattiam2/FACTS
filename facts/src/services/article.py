import hashlib
import json
import random
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

import rlp
from eth_account._utils.legacy_transactions import Transaction
from fastapi import Depends

from facts.src.core.auth import User
from facts.src.core.config import settings
from facts.src.core.exceptions import FACTSError, FACTSDuplicateError, FACTSAuthError, FACTSNotFoundError, \
    FACTSRequestError
from facts.src.repositories.ebsi_tnt import TntRepository
from facts.src.repositories.facts import ArticleRepository
from facts.src.schemas.article import ArticlePayload
from facts.src.schemas.shared import BuildTransactionResponse, SignedTransactionPayload, \
    SignedTransactionResponse


class ArticleServiceError(FACTSError):
    """
    Represents an error specific to Article service operations (Status Code: 500).
    """
    pass


class ArticleServiceDuplicateError(ArticleServiceError, FACTSDuplicateError):
    """
    Represents an error raised when a duplicate entry is detected (Status Code: 409).
    """
    pass


class ArticleServiceAuthError(ArticleServiceError, FACTSAuthError):
    """
    Represents an Article service authentication error (Status Code: 401).
    """
    pass


class ArticleServiceNotFoundError(ArticleServiceError, FACTSNotFoundError):
    """
    Represents an error raised when a specific resource is not found (Status Code: 404).
    """
    pass


class ArticleServiceRequestError(ArticleServiceError, FACTSRequestError):
    """
    Represents an error that occurs during an Article service request.
    """
    pass


class ArticleService:
    tnt_repository: TntRepository
    article_repository: ArticleRepository

    def __init__(self, tnt_repository: TntRepository = Depends(), article_repository: ArticleRepository = Depends()):
        self.tnt_repository = tnt_repository
        self.article_repository = article_repository

    @classmethod
    def normalize_url(cls, url: str) -> str:
        """
        Normalizes a URL to ensure that identical URLs produce the same hash.

        :param url: The URL to normalize.
        :type url: str
        :return: The normalized URL string.
        :rtype: str
        """
        # Parse the URL into components
        url_to_parse = url.strip()
        if not url_to_parse.startswith("http"):
            url_to_parse = "//" + url_to_parse

        parsed = urlsplit(url_to_parse)
        host = parsed.netloc.lower()
        if ":" in host:
            host, port = host.rsplit(':', 1)

        path = parsed.path
        if path and path != '/' and path.endswith('/'):
            path = path.rstrip('/')
        if not path:
            path = '/'

        query_params = parse_qs(parsed.query, keep_blank_values=False)
        filtered_query_params = {key: value for key, value in query_params.items() if
                                 key not in settings.TRACKER_PARAMS}
        sorted_query = urlencode(sorted(filtered_query_params.items()), doseq=True)

        normalized = urlunsplit(('', host, path, sorted_query, ''))

        return normalized

    def hash_url(self, url: str):
        normalized_url = ArticleService.normalize_url(url)
        document_hash = "0x" + hashlib.sha256(normalized_url.encode()).hexdigest()
        return document_hash

    def get_article_by_url(self, url: str):
        """
        Retrieves an article based on its url.
        """
        document_hash = self.hash_url(url)
        document_element = self.tnt_repository.get_document(document_hash)
        return document_element.metadata_json if document_element.metadata_json else None

    def request_create_article(self, user: User, payload: ArticlePayload):
        normalized_url = ArticleService.normalize_url(payload.article_metadata.article_info.url)
        document_hash = self.hash_url(payload.article_metadata.article_info.url)
        user_did = user.credential_subject.id
        user_vc = user.verifiable_credential
        ebsi_access_token = user.ebsi_access_token

        build_response = self.build_create_transaction(user_did, user_vc, ebsi_access_token, document_hash, payload)
        transaction: dict = build_response.transaction

        unsigned_transaction_data = bytes.fromhex(transaction['data'].replace("0x", ""))
        data_hash = hashlib.sha256(unsigned_transaction_data).hexdigest()
        self.article_repository.create(hash=document_hash, url=normalized_url, creator=user_did, tx_hash=None, data_hash=data_hash, confirmed=False)
        return build_response

    def confirm_create_article(self, user: User, document_hash: str, transaction: SignedTransactionPayload):
        unconfirmed_article = self.article_repository.get(document_hash)
        if unconfirmed_article is None:
            raise ArticleServiceNotFoundError(f"Article with hash {document_hash} not found")
        if unconfirmed_article.confirmed:
            raise ArticleServiceRequestError("Article already confirmed")
        if unconfirmed_article.creator != user.credential_subject.id:
            raise ArticleServiceRequestError("User does not own the article")
        signed_transaction_bytes = bytes.fromhex(transaction.signedRawTransaction)
        signed_decoded_transaction: Transaction = rlp.decode(signed_transaction_bytes, Transaction)
        signed_transaction_data = signed_decoded_transaction['data']
        signed_data_hash = hashlib.sha256(signed_transaction_data).hexdigest()
        if unconfirmed_article.data_hash != signed_data_hash:
            raise ArticleServiceRequestError("Transaction data hash does not match the expected hash")
        signed_transaction_response = self.send_signed_transaction(user, transaction)
        if signed_transaction_response.transaction_hash is not None:
            self.article_repository.update(id=document_hash, confirmed=True, tx_hash=signed_transaction_response.transaction_hash)
        return signed_transaction_response

    def build_create_transaction(self, user_did: str, user_vc: str, ebsi_access_token: str, document_hash: str, payload: ArticlePayload) -> BuildTransactionResponse:
        transaction_id = random.randint(1, 999)
        document_metadata = payload.article_metadata.model_dump(mode="json")
        document_metadata["publisher_vc"] = user_vc
        document_metadata_string = json.dumps(document_metadata)
        document_metadata_hex = "0x" + document_metadata_string.encode().hex()
        json_rpc_response = self.tnt_repository.build_document_transaction(access_token=ebsi_access_token,
                                                                           from_eth_address=payload.from_eth_address,
                                                                           transaction_id=transaction_id,
                                                                           doc_hash=document_hash,
                                                                           doc_metadata=document_metadata_hex,
                                                                           did_ebsi_creator=user_did)
        return BuildTransactionResponse(document_hash=document_hash, transaction=json_rpc_response[
            "result"] if "result" in json_rpc_response else None)

    def send_signed_transaction(self, user: User, transaction: SignedTransactionPayload):
        transaction_dict = transaction.model_dump(mode="json")
        json_rpc_response = self.tnt_repository.send_signed_transaction(access_token=user.ebsi_access_token,
                                                                        transaction=transaction_dict)
        return SignedTransactionResponse(
            transaction_hash=json_rpc_response["result"] if "result" in json_rpc_response else None)
