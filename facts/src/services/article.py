import hashlib
import random
import rlp
from eth_account._utils.legacy_transactions import Transaction
from fastapi import Depends

from facts.src import utils
from facts.src.core.auth import User
from facts.src.core.exceptions import FACTSError, FACTSDuplicateError, FACTSAuthError, FACTSNotFoundError, \
    FACTSRequestError
from facts.src.repositories.ebsi_tnt import TntClient
from facts.src.repositories.facts import ArticleRepository
from facts.src.schemas.article import ArticleCreate, ArticleMetadataPublic, ArticleSourceChainPublic
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
    tnt_client: TntClient
    article_repository: ArticleRepository

    def __init__(self, tnt_client: TntClient = Depends(), article_repository: ArticleRepository = Depends()):
        self.tnt_client = tnt_client
        self.article_repository = article_repository

    def get_article_by_hash(self, document_hash: str):
        facts_article = self.article_repository.get(document_hash)
        if not facts_article or not facts_article.confirmed:
            raise ArticleServiceNotFoundError(f"Article with hash {document_hash} not found")
        return self.tnt_client.get_document(document_hash)

    def get_article_by_url(self, url: str):
        """
        Retrieves an article based on its url.
        """
        document_hash = utils.hash_url(url)
        document_element = self.get_article_by_hash(document_hash)
        return document_element.metadata_json if document_element.metadata_json else None

    def get_article_sources_chain(self, article_hash: str):
        article = self.article_repository.get(article_hash)
        if not article:
            raise ArticleServiceNotFoundError(f"Article with hash {article_hash} not found")
        sources_nodes = self.article_repository.get_source_chain(article_hash, 10)
        response = ArticleSourceChainPublic.model_validate({
            'root_article_hash': article_hash,
            'max_depth': 10,
            'nodes': sources_nodes
        })
        return response


    def get_articles_list(self, did_creator: str | None = None, offset: int = 0, page_size: int = 100):
        articles = self.article_repository.list(creator=did_creator, confirmed=True, offset=offset, limit=page_size, order_by="timestamp")
        return articles

    @classmethod
    def check_authorized_hosts(cls, article_url: str, authorized_hosts: list[str]):
        normalized_url = utils.normalize_url(article_url)
        host, _, _ = utils.split_url(normalized_url)
        return host in authorized_hosts

    def request_create_article(self, user: User, payload: ArticleCreate):
        is_authorized = self.check_authorized_hosts(payload.article_info.url, user.credential_subject.authorized_hosts)

        if not is_authorized:
            raise ArticleServiceAuthError("Forbidden host")

        normalized_url = utils.normalize_url(payload.article_info.url)

        document_hash = utils.hash_url(payload.article_info.url)

        existing_article = self.article_repository.get(document_hash)
        if existing_article and existing_article.confirmed:
            raise ArticleServiceDuplicateError(f"Article with URL {normalized_url} already exists")
        elif existing_article and not existing_article.confirmed:
            self.article_repository.delete(id=document_hash)

        from_eth_address = payload.from_eth_address
        user_did = user.credential_subject.id
        user_vc = user.verifiable_credential
        ebsi_access_token = user.ebsi_access_token

        article_metadata = ArticleMetadataPublic(version="1.0", article_info=payload.article_info, eth_address=from_eth_address, publisher_vc=user_vc)

        build_response = self.build_create_transaction(from_eth_address, user_did, ebsi_access_token, document_hash, article_metadata)
        transaction: dict = build_response.transaction

        unsigned_transaction_data = bytes.fromhex(transaction['data'].replace("0x", ""))
        data_hash = hashlib.sha256(unsigned_transaction_data).hexdigest()
        self.article_repository.create(hash=document_hash, url=normalized_url, creator=user_did, tx_hash=None, data_hash=data_hash, eth_address=from_eth_address, confirmed=False)
        for source_value in payload.article_info.sources:
            source_hash = None
            if source_value.startswith("http"):
                source_hash = utils.hash_url(source_value)
                source_value = utils.normalize_url(source_value)
            self.article_repository.add_source(article_hash=document_hash, source_value=source_value, source_hash=source_hash)
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

    def build_create_transaction(self, from_eth_address: str, user_did: str, ebsi_access_token: str, document_hash: str, payload: ArticleMetadataPublic) -> BuildTransactionResponse:
        return utils.build_create_transaction(self.tnt_client, from_eth_address, user_did, ebsi_access_token, document_hash, payload=payload)

    def send_signed_transaction(self, user: User, transaction: SignedTransactionPayload):
        return utils.send_signed_transaction(self.tnt_client, user, transaction)
