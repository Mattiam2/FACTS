import hashlib
from urllib.parse import urlunsplit, urlsplit, parse_qs, urlencode

from facts.src.core.config import settings

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
    normalized = urlunsplit(('', host, path, sorted_query, ''))

    return normalized


def hash_url(url: str):
    normalized_url = normalize_url(url)
    full_hashable_content = "FACTS_ARTICLE:" + normalized_url
    document_hash = "0x" + hashlib.sha256(full_hashable_content.encode()).hexdigest()
    return document_hash
