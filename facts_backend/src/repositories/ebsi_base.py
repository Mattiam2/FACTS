import httpx

from facts_backend.src.core.config import settings
from facts_backend.src.core.exceptions import FACTSError, FACTSRequestError, FACTSAuthError, FACTSNotFoundError, \
    FACTSDuplicateError


class EBSIError(FACTSError):
    """
    Represents an error specific to the EBSI Client.
    """
    pass

class EBSIRequestError(EBSIError, FACTSRequestError):
    """
    Represents a generic EBSI request error (Status Code: 400).
    """
    pass

class EBSIAuthError(EBSIError, FACTSAuthError):
    """
    Represents an authentication error specific to EBSI (Status Code: 401).
    """
    pass

class EBSINotFoundError(EBSIError, FACTSNotFoundError):
    """
    Represents a specific error when an EBSI record is not found (Status Code: 404).
    """
    pass

class EBSIDuplicateError(EBSIError, FACTSDuplicateError):
    """
    Exception raised for duplicate errors specific to EBSI (Status Code: 409).
    """
    pass

class EBSIClient:
    client: httpx.Client

    def __init__(self, root_path: str):
        """
        Initializes an instance of the class with a specific root path and creates
        an HTTP client towards EBSI for interacting with the base URL derived from the provided
        root path.

        :param root_path: The root path to be appended to the base EBSI URL. Used to
            configure the client's base URL.
        :type root_path: str
        """
        base_url = f"{settings.EBSI_URL}/{root_path}"
        self.client = httpx.Client(base_url=base_url, timeout=100.0)

    def get(self, path: str, params: dict = None):
        """
        Sends a GET request to the specified path with optional query parameters and
        returns the parsed JSON response.

        :param path: The API endpoint path to which the GET request will be sent.
        :param params: A dictionary of query parameters to include in the request
            (defaults to None).
        :return: The parsed JSON response from the GET request.
        :rtype: dict
        :raises HTTPError: If the response status code indicates an HTTP error.
        """
        with self.client as client:
            try:
                response = client.get(path, params=params)
                response.raise_for_status()
            except httpx.HTTPError:
                if response:
                    message = response.json().get("detail", response)
                    if response.status_code == 400:
                        raise EBSIRequestError(f"Error calling EBSI API {path}: {message}")
                    elif response.status_code == 401:
                        raise EBSIAuthError(f"Error calling EBSI API {path}: {message}")
                    elif response.status_code == 404:
                        raise EBSINotFoundError(f"Error calling EBSI API {path}: {message}")
                    elif response.status_code == 409:
                        raise EBSIDuplicateError(f"Error calling EBSI API {path}: {message}")
                    else:
                        raise EBSIError(f"Error calling EBSI API {path}: {message}")
                raise EBSIError(f"Error calling EBSI API {path}")
            return response.json()

    def post(self, path: str, *, data: dict, access_token: str | None = None):
        """
        Posts JSON data to a specified API path using a provided HTTP client. Handles various HTTP
        errors and raises appropriate exceptions based on the status code and error details returned
        by the API.

        :param path: The API endpoint path to which the POST request will be sent.
        :type path: str
        :param data: The dictionary containing the JSON payload to be sent with the POST request.
        :type data: dict
        :param access_token: Optional bearer token for API authentication. If provided, it will be
            included in the Authorization header.
        :type access_token: str | None
        :return: The JSON-decoded response from the API.
        :rtype: dict
        :raises EBSIRequestError: If the API responds with a 400 Bad Request error.
        :raises EBSIAuthError: If the API responds with a 401 Unauthorized error.
        :raises EBSINotFoundError: If the API responds with a 404 Not Found error.
        :raises EBSIDuplicateError: If the API responds with a 409 Conflict error.
        :raises EBSIError: If any other error occurs while calling the API or if the response does
            not include an expected error detail.
        """
        with self.client as client:
            response = None
            try:
                headers = {"Content-Type": "application/json"}
                if access_token:
                    headers["Authorization"] = f"Bearer {access_token}"
                response = client.post(path, json=data, headers=headers)
                response.raise_for_status()
            except httpx.HTTPError:
                if response:
                    message = response.json().get("detail", response)
                    if response.status_code == 400:
                        raise EBSIRequestError(f"Error calling EBSI API {path}: {message}")
                    elif response.status_code == 401:
                        raise EBSIAuthError(f"Error calling EBSI API {path}: {message}")
                    elif response.status_code == 404:
                        raise EBSINotFoundError(f"Error calling EBSI API {path}: {message}")
                    elif response.status_code == 409:
                        raise EBSIDuplicateError(f"Error calling EBSI API {path}: {message}")
                    else:
                        raise EBSIError(f"Error calling EBSI API {path}: {message}")
                raise EBSIError(f"Error calling EBSI API {path}")
            return response.json()
