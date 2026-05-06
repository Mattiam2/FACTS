from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends

from facts.src.core.auth import User
from facts.src.core.config import settings
from facts.src.core.exceptions import FACTSError, FACTSDuplicateError, FACTSAuthError, FACTSNotFoundError, \
    FACTSRequestError
from facts.src.repositories.ebsi_auth import AuthClient
from facts.src.schemas.auth import TokenScopeEnum, EBSITokenPublic, TokenPublic
from facts.src.schemas.verifiable_credential import VerifiableCredentialPayload
from facts.src.schemas.verifiable_presentation import VerifiablePresentationPayload


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
    auth_client: AuthClient

    def __init__(self, auth_client: AuthClient = Depends()):
        self.auth_client = auth_client

    def request_token(self, vp_token: str, scope: TokenScopeEnum) -> TokenPublic:
        vp_token_decoded = jwt.decode(vp_token, options={"verify_signature": False, "verify_exp": False})
        vp_token_object = VerifiablePresentationPayload.model_validate(vp_token_decoded)

        if vp_token_object.exp < datetime.now().timestamp():
            raise FACTSAuthError("VP Token expired")

        if vp_token_object.vp is None or vp_token_object.vp.verifiableCredential is None:
            raise FACTSAuthError("Invalid VP Token")

        vc_token = vp_token_object.vp.verifiableCredential[0]
        vc_token_decoded = jwt.decode(vc_token, options={"verify_signature": False, "verify_exp": False})
        vc_token_object = VerifiableCredentialPayload.model_validate(vc_token_decoded)
        credential_types = vc_token_object.vc.type
        credential_object = vc_token_object.vc.credentialSubject

        if scope == TokenScopeEnum.scope_publisher_write and "FACTSPublisherCredential" in credential_types:
            presentation_scope = "openid tnt_write"
            presentation_id = "tnt_write_presentation"
        elif scope == TokenScopeEnum.scope_publisher_create and "FACTSPublisherCredential" in credential_types:
            presentation_scope = "openid tnt_create"
            presentation_id = "tnt_create_presentation"
        elif scope == TokenScopeEnum.scope_factchecker_create and "FACTSFactCheckerCredential" in credential_types:
            presentation_scope = "openid tnt_create"
            presentation_id = "tnt_create_presentation"
        elif scope == TokenScopeEnum.scope_factchecker_write and "FACTSFactCheckerCredential" in credential_types:
            presentation_scope = "openid tnt_write"
            presentation_id = "tnt_write_presentation"
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

        ebsi_token_data: EBSITokenPublic = self.auth_client.get_token(data=authorisation_payload)
        user_dict = {
            "ebsi_access_token": ebsi_token_data.access_token,
            "scopes": [scope.value],
            "credential_subject": credential_object,
            "verifiable_credential": vc_token
        }
        user = User.model_validate(user_dict)

        facts_access_token = self.create_access_token(user.model_dump(), expires_delta=timedelta(minutes=120))
        token_data = TokenPublic(access_token=facts_access_token, token_type="Bearer")
        return token_data

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.AUTH_SECRET_KEY, algorithm="HS256")
        return encoded_jwt