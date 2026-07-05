import hashlib

import rlp
from eth_account._utils.legacy_transactions import Transaction
from fastapi import Depends

from facts_backend.src import utils
from facts_backend.src.core.auth import User
from facts_backend.src.core.exceptions import FACTSError, FACTSDuplicateError, FACTSAuthError, FACTSNotFoundError, \
    FACTSRequestError
from facts_backend.src.repositories.ebsi_tnt import TntClient
from facts_backend.src.repositories.facts import ArticleRepository
from facts_backend.src.schemas.article import ArticleCreate, ArticleMetadataPublic, ArticleSourceChainPublic
from facts_backend.src.schemas.shared import BuildTransactionResponse, SignedTransactionPayload


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
        """
        Fetches an article from the FACTS DB by its hash identifier. If the article is not found or is not
        marked as confirmed in the system, an exception is raised. The retrieved article is then
        fetched from EBSI TNT API.

        :param document_hash: The unique hash that identifies the article.
        :type document_hash: str

        :return: The article obtained from EBSI TNT API

        :raises ArticleServiceNotFoundError: If the article is not found or is not confirmed.
        """
        facts_article = self.article_repository.get(document_hash)
        if not facts_article or not facts_article.confirmed:
            raise ArticleServiceNotFoundError(f"Article with hash {document_hash} not found")
        return self.tnt_client.get_document(document_hash)

    def head_article_by_url(self, url: str):
        """
        Checks if an article exists in the repository based on its URL.

        :param url: URL of the article to be checked
        :type url: str
        :return: True if the article exists in the repository, otherwise False.
        :rtype: bool
        """
        document_hash = utils.hash_url(url)
        document_element = self.article_repository.get(document_hash)
        return document_element is not None


    def get_article_by_url(self, url: str):
        """
        Fetches an article based on its URL.

        This method computes a document hash from the given URL and retrieves the
        corresponding article using that hash. If no article is found for the
        calculated hash, it returns None.

        :param url: The URL of the article to be retrieved.
        :type url: str
        :return: The retrieved article element if found
        """
        document_hash = utils.hash_url(url)
        document_element = self.get_article_by_hash(document_hash)
        return document_element

    def get_article_sources_chain(self, article_hash: str):
        """
        Fetches the chain of source articles for a given article identified by its hash.

        :param article_hash: The hash identifying the article.
        :type article_hash: str
        :return: Object containing the source chain details including the root article hash, the maximum depth of the chain,
                 and the source nodes.
        :rtype: ArticleSourceChainPublic
        :raises ArticleServiceNotFoundError: If the article is not found or is not confirmed.
        """
        max_depth = 10
        article = self.article_repository.get(article_hash)
        if not article or not article.confirmed:
            raise ArticleServiceNotFoundError(f"Article with hash {article_hash} not found")
        sources_nodes = self.article_repository.get_source_chain(article_hash, max_depth)

        response = ArticleSourceChainPublic.model_validate({
            'root_article_hash': article_hash,
            'max_depth': max_depth,
            'nodes': sources_nodes
        })
        return response


    def get_articles_list(self, did_creator: str | None = None, offset: int = 0, page_size: int = 100):
        """
        Fetches a paginated list of articles created by a specific user or all confirmed articles if no creator is specified.

        :param did_creator: Optional DID creator for filtering articles by a specific user. If None, retrieves articles from all users.
        :type did_creator: str | None
        :param offset: The starting position of the articles to be fetched. Defaults to 0.
        :type offset: int
        :param page_size: The maximum number of articles to retrieve in a single query. Defaults to 100.
        :type page_size: int
        :return: A list of articles matching the filtering and pagination criteria.
        :rtype: list
        """
        articles = self.article_repository.list(creator=did_creator, confirmed=True, offset=offset, limit=page_size, order_by="timestamp")
        return articles

    @classmethod
    def check_authorized_hosts(cls, article_url: str, authorized_hosts: list[str]):
        """
        Checks if the host of a given article URL is within the list of authorized hosts.

        :param article_url: The URL of the article to check.
        :param authorized_hosts: A list of hosts that are considered authorized.
        :return: A boolean indicating whether the article's host is authorized.
        :rtype: bool
        """
        normalized_url = utils.normalize_url(article_url)
        host, _, _ = utils.split_url(normalized_url)
        return host in authorized_hosts

    def request_create_article(self, user: User, payload: ArticleCreate):
        """
        Creates a new article entry in the system and initiates the process for
        building a transaction for the article data. This function verifies host
        authorization, checks for duplications and normalizes the article's URL

        :param user: The user initiating the request. The user must have valid
            credential attributes like `credential_subject.id`, `credential_subject.authorized_hosts`,
            `verifiable_credential`, and `ebsi_access_token`.
        :type user: User
        :param payload: Contains the article creation data, including the article's
            information, sources, and associated Ethereum address.
        :type payload: ArticleCreate
        :return: A response object containing the created transaction details.
        :rtype: dict
        :raises ArticleServiceAuthError: If the host specified in the article's URL
            is not in the user's authorized hosts.
        :raises ArticleServiceDuplicateError: If an existing article with the normalized
            URL is already confirmed in the system.
        """
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
        """
        Confirms and finalizes the creation of an article by validating the provided signed transaction payload
        and user ownership, ensuring the article metadata matches the associated transaction data hash,
        and sending the signed transaction to the blockchain.

        :param user: The user attempting to confirm the creation of the article. Must match the creator
            of the unconfirmed article in the repository.
        :type user: User
        :param document_hash: The unique hash of the unconfirmed article to be confirmed.
        :type document_hash: str
        :param transaction: The payload containing the signed transaction intended for confirmation.
        :type transaction: SignedTransactionPayload
        :return: The response from the blockchain containing confirmation details, including the
            transaction hash.
        :rtype: SignedTransactionResponse
        :raises ArticleServiceNotFoundError: If no unconfirmed article exists with the provided hash.
        :raises ArticleServiceRequestError: If the article is already confirmed, the user is not the owner,
            or the transaction data hash does not match the expected hash.
        """
        unconfirmed_article = self.article_repository.get(document_hash)
        if unconfirmed_article is None:
            raise ArticleServiceNotFoundError(f"Article with hash {document_hash} not found")
        if unconfirmed_article.confirmed:
            raise ArticleServiceRequestError("Article already confirmed")
        if unconfirmed_article.creator != user.credential_subject.id:
            raise ArticleServiceRequestError("User does not own the article")
        signed_transaction_bytes = bytes.fromhex(transaction.signedRawTransaction.replace("0x", ""))
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
        """
        Builds a transaction for creating an on-chain record using the specified parameters.

        :param from_eth_address: The Ethereum from address.
        :type from_eth_address: str
        :param user_did: The DID of the user initiating the transaction.
        :type user_did: str
        :param ebsi_access_token: The access token for interacting with the EBSI.
        :type ebsi_access_token: str
        :param document_hash: The hash of the article to be written to the blockchain.
        :type document_hash: str
        :param payload: Metadata describing the article, to be included in the transaction payload.
        :type payload: ArticleMetadataPublic
        :return: A response object containing the details of the constructed
                 transaction.
        :rtype: BuildTransactionResponse
        """
        return utils.build_create_transaction(self.tnt_client, from_eth_address, user_did, ebsi_access_token, document_hash, payload=payload)

    def send_signed_transaction(self, user: User, transaction: SignedTransactionPayload):
        """
        Sends a signed transaction using the provided user and transaction details.

        :param user: The user initiating the transaction.
        :type user: User
        :param transaction: The signed transaction payload to be sent.
        :type transaction: SignedTransactionPayload
        :return: The result of the transaction processing.
        :rtype: Any
        """
        return utils.send_signed_transaction(self.tnt_client, user, transaction)
