import httpx

from facts_backend.src.core.config import settings
from facts_backend.src.core.exceptions import FACTSError, FACTSRequestError, FACTSAuthError, FACTSNotFoundError, \
    FACTSDuplicateError


class EBSIError(FACTSError):
    pass

class EBSIRequestError(EBSIError, FACTSRequestError):
    pass

class EBSIAuthError(EBSIError, FACTSAuthError):
    pass

class EBSINotFoundError(EBSIError, FACTSNotFoundError):
    pass

class EBSIDuplicateError(EBSIError, FACTSDuplicateError):
    pass

class EBSIClient:
    client: httpx.Client

    def __init__(self, root_path: str):
        base_url = f"{settings.EBSI_URL}/{root_path}"
        self.client = httpx.Client(base_url=base_url, timeout=100.0)

    def get(self, path: str, params: dict = None):
        with self.client as client:
            response = client.get(path, params=params)
            response.raise_for_status()
            return response.json()

    def post(self, path: str, *, data: dict, access_token: str | None = None):
        with self.client as client:
            response = None
            try:
                headers = {"Content-Type": "application/json"}
                if access_token:
                    headers["Authorization"] = f"Bearer {access_token}"
                response = client.post(path, json=data, headers=headers)
                response.raise_for_status()
            except httpx.HTTPError:
                message = "unknown error"
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
