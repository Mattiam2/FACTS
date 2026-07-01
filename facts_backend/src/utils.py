import hashlib
import random
from urllib.parse import urlunsplit, urlsplit, parse_qs, urlencode

from facts_backend.src.core.auth import User
from facts_backend.src.core.config import settings
from facts_backend.src.repositories.ebsi_tnt import TntClient
from facts_backend.src.schemas.article import ArticleMetadataPublic
from facts_backend.src.schemas.assessment import AssessmentMetadataPublic
from facts_backend.src.schemas.shared import BuildTransactionResponse, SignedTransactionPayload, \
    SignedTransactionResponse


def split_url(url: str) -> tuple[str, str, str]:
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
    return host, path, sorted_query

def normalize_url(url: str) -> str:
    """
    Normalizes a URL to ensure that identical URLs produce the same hash.

    :param url: The URL to normalize.
    :type url: str
    :return: The normalized URL string.
    :rtype: str
    """
    host, path, sorted_query = split_url(url)
    host = host.replace('www.', '')
    path = path.rstrip('/')
    normalized = urlunsplit(('https', host, path, sorted_query, ''))

    return normalized


def hash_url(url: str):
    normalized_url = normalize_url(url)
    full_hashable_content = "FACTS_ARTICLE:" + normalized_url
    document_hash = "0x" + hashlib.sha256(full_hashable_content.encode()).hexdigest()
    return document_hash


def build_create_transaction(tnt_client: TntClient, from_eth_address: str, user_did: str, ebsi_access_token: str, document_hash: str, payload: AssessmentMetadataPublic | ArticleMetadataPublic) -> BuildTransactionResponse:
    transaction_id = random.randint(1, 999)
    document_metadata_json = payload.model_dump_json(by_alias=True)
    document_metadata_hex = "0x" + document_metadata_json.encode().hex()
    json_rpc_response = tnt_client.build_document_transaction(access_token=ebsi_access_token,
                                                                   from_eth_address=from_eth_address,
                                                                   transaction_id=transaction_id,
                                                                   doc_hash=document_hash,
                                                                   doc_metadata=document_metadata_hex,
                                                                   did_ebsi_creator=user_did)
    return BuildTransactionResponse(document_hash=document_hash, transaction=json_rpc_response[
        "result"] if "result" in json_rpc_response else None)

def send_signed_transaction(tnt_client: TntClient, user: User, transaction: SignedTransactionPayload):
    transaction_dict = transaction.model_dump(mode="json")
    json_rpc_response = tnt_client.send_signed_transaction(access_token=user.ebsi_access_token,
                                                                transaction=transaction_dict)
    return SignedTransactionResponse(
        transaction_hash=json_rpc_response["result"] if "result" in json_rpc_response else None)