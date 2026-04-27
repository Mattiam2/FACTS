from datetime import datetime

import jwt
from fastapi import Depends

from facts_publish.src.core.exceptions import FACTSError, FACTSDuplicateError, FACTSAuthError, FACTSNotFoundError, \
    FACTSRequestError
from facts_publish.src.repositories.ebsi_auth import AuthRepository
from facts_publish.src.schemas.auth import TokenRequestScopeEnum, TokenPublic


class AuthServiceError(FACTSError):
    """
    Represents an error specific to Article service operations (Status Code: 500).
    """
    pass


class AuthServiceDuplicateError(AuthServiceError, FACTSDuplicateError):
    """
    Represents an error raised when a duplicate entry is detected (Status Code: 409).
    """
    pass


class AuthServiceAuthError(AuthServiceError, FACTSAuthError):
    """
    Represents an Article service authentication error (Status Code: 401).
    """
    pass


class AuthServiceNotFoundError(AuthServiceError, FACTSNotFoundError):
    """
    Represents an error raised when a specific resource is not found (Status Code: 404).
    """
    pass


class AuthServiceRequestError(AuthServiceError, FACTSRequestError):
    """
    Represents an error that occurs during an Article service request.
    """
    pass


class AuthService:
    auth_repository: AuthRepository

    def __init__(self, auth_repository: AuthRepository = Depends()):
        self.auth_repository = auth_repository

    def request_token(self, vp_token: str, scope: TokenRequestScopeEnum) -> TokenPublic:
        vp_token_decoded = jwt.decode(vp_token, options={"verify_signature": False, "verify_exp": False})
        is_token_expired = vp_token_decoded.get(
            "exp") < datetime.now().timestamp()

        if is_token_expired:
            raise FACTSAuthError("VP Token expired")

        if scope == TokenRequestScopeEnum.scope_write:
            presentation_scope = "openid tnt_write"
            presentation_id = "tnt_write_presentation"
        elif scope == TokenRequestScopeEnum.scope_create:
            presentation_scope = "openid tnt_create"
            presentation_id = "tnt_create_presentation"
        else:
            raise AuthServiceRequestError("Invalid scope")

        authorisation_payload = {
            "grant_type": "vp_token",
            "vp_token": vp_token,
            "presentation_submission": {
                "definition_id": presentation_id,
                "descriptor_map": [],
                "id": "ac9026c2-c3f5-4a26-b609-ec215cf97ba2"
            },
            "scope": presentation_scope
        }

        token_data = self.auth_repository.get_token(data=authorisation_payload)
        return token_data
