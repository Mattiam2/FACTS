import hashlib
import json
import time
from datetime import datetime
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode, urlsplit, urlunsplit

from fastapi import Depends
from web3 import Web3
from web3.contract import Contract

from facts_publish.src.core.config import settings
from facts_publish.src.core.exceptions import FACTSError, FACTSDuplicateError, FACTSAuthError, FACTSNotFoundError, \
    FACTSRequestError
from facts_publish.src.repositories.ebsi_tnt import TntRepository
from facts_publish.src.schemas.article import ArticlePayload


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
        filtered_query_params = {key: value for key, value in query_params.items() if key not in settings.TRACKER_PARAMS}
        sorted_query = urlencode(sorted(filtered_query_params.items()), doseq=True)

        normalized = urlunsplit(('', host, path, sorted_query, ''))


        return normalized

    def get_article_by_url(self, url: str):
        """
        Retrieves an article based on its url.
        """

        normalized_url = ArticleService.normalize_url(url)

        document_hash = "0x" + hashlib.sha256(normalized_url.encode()).hexdigest()
        document_element = self.tnt_repository.get_document(document_hash)
        return document_element.metadata_json if document_element.metadata_json else None

    def build_transaction(self, payload: ArticlePayload):
        self.tnt_repository.build_document_transaction("pippo")
