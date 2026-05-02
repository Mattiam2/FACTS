import hashlib
import json
import random
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from fastapi import Depends

from facts_backoffice.src.core.auth import User
from facts_backoffice.src.core.config import settings
from facts_backoffice.src.core.exceptions import FACTSError, FACTSDuplicateError, FACTSAuthError, FACTSNotFoundError, \
    FACTSRequestError
from facts_backoffice.src.repositories.ebsi_tnt import TntRepository
from facts_backoffice.src.schemas.article import ArticlePayload
from facts_backoffice.src.schemas.shared import BuildTransactionResponse, SignedTransactionPayload, \
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

    def __init__(self, tnt_repository: TntRepository = Depends()):
        self.tnt_repository = tnt_repository

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

    def build_create_transaction(self, user: User, payload: ArticlePayload) -> BuildTransactionResponse:
        document_hash = self.hash_url(payload.article_metadata.article_info.url)
        transaction_id = random.randint(1, 999)
        did_ebsi_creator = user.credential_subject.id
        publisher_vc = user.verifiable_credential
        document_metadata = payload.article_metadata.model_dump(mode="json")
        document_metadata["publisher_vc"] = publisher_vc
        document_metadata_string = json.dumps(document_metadata)
        document_metadata_hex = "0x" + document_metadata_string.encode().hex()
        json_rpc_response = self.tnt_repository.build_document_transaction(access_token=user.ebsi_access_token,
                                                       from_eth_address=payload.from_eth_address,
                                                       transaction_id=transaction_id, doc_hash=document_hash,
                                                       doc_metadata=document_metadata_hex,
                                                       did_ebsi_creator=did_ebsi_creator)
        return BuildTransactionResponse(document_hash=document_hash, transaction=json_rpc_response["result"] if "result" in json_rpc_response else None)

    def send_signed_transaction(self, user: User, transaction: SignedTransactionPayload):
        transaction_dict = transaction.model_dump(mode="json")
        json_rpc_response = self.tnt_repository.send_signed_transaction(access_token=user.ebsi_access_token, transaction=transaction_dict)
        return SignedTransactionResponse(transaction_hash=json_rpc_response["result"] if "result" in json_rpc_response else None)