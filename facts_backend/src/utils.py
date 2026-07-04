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
    """
    Splits a given URL into its components: host, path, and sorted query string. The
    function processes the input URL, ensures proper formatting, and filters unwanted
    query parameters based on pre-defined configurations.

    :param url: The URL string to be parsed.
    :type url: str
    :return: A tuple containing the host, processed path, and sorted query string.
    :rtype: tuple[str, str, str]
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
    """
    Generates a unique hash for a given URL.

    :param url: The URL to be hashed.
    :type url: str
    :return: A unique document hash in hexadecimal format prefixed with "0x".
    :rtype: str
    """
    normalized_url = normalize_url(url)
    full_hashable_content = "FACTS_ARTICLE:" + normalized_url
    document_hash = "0x" + hashlib.sha256(full_hashable_content.encode()).hexdigest()
    return document_hash


def build_create_transaction(tnt_client: TntClient, from_eth_address: str, user_did: str, ebsi_access_token: str, document_hash: str, payload: AssessmentMetadataPublic | ArticleMetadataPublic) -> BuildTransactionResponse:
    """
    Builds a transaction for TNT document management using the provided client and metadata.

    :param tnt_client: Client instance used to build document transactions.
    :type tnt_client: TntClient
    :param from_eth_address: Ethereum address of the transaction's sender.
    :type from_eth_address: str
    :param user_did: Decentralized Identifier (DID) of the transaction creator.
    :type user_did: str
    :param ebsi_access_token: Token used for authentication on the EBSI network.
    :type ebsi_access_token: str
    :param document_hash: Hash of the document being referenced in the transaction.
    :type document_hash: str
    :param payload: Metadata of the TNT document.
    :type payload: AssessmentMetadataPublic | ArticleMetadataPublic
    :return: Response containing the document hash and the result of the JSON-RPC transaction.
    :rtype: BuildTransactionResponse
    """
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
    """
    Send a signed transaction to the TNT client.

    The response from the TNT client is converted into a
    `SignedTransactionResponse` object containing the transaction hash
    if it is available in the response.

    :param tnt_client: An instance of the TNT client that handles the
        interaction with the remote system.
    :type tnt_client: TntClient
    :param user: An object representing a user, which contains the required
        access token for authenticating the transaction.
    :type user: User
    :param transaction: A signed transaction payload object representing
        the data to be sent via the TNT client.
    :type transaction: SignedTransactionPayload
    :return: A response object encapsulating the result of the transaction,
        including the transaction hash if it is available.
    :rtype: SignedTransactionResponse
    """
    transaction_dict = transaction.model_dump(mode="json")
    json_rpc_response = tnt_client.send_signed_transaction(access_token=user.ebsi_access_token,
                                                                transaction=transaction_dict)
    return SignedTransactionResponse(
        transaction_hash=json_rpc_response["result"] if "result" in json_rpc_response else None)