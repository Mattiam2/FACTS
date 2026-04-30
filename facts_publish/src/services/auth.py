from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends

from facts_publish.src.core.auth import User
from facts_publish.src.core.config import settings
from facts_publish.src.core.exceptions import FACTSError, FACTSDuplicateError, FACTSAuthError, FACTSNotFoundError, \
    FACTSRequestError
from facts_publish.src.repositories.ebsi_auth import AuthRepository
from facts_publish.src.schemas.auth import TokenScopeEnum, EBSITokenPublic, TokenPublic
from facts_publish.src.schemas.verifiable_credential import VerifiableCredentialPayload
from facts_publish.src.schemas.verifiable_presentation import VerifiablePresentationPayload


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

    def request_token(self, vp_token: str, scope: TokenScopeEnum) -> TokenPublic:
        vp_token_decoded = jwt.decode(vp_token, options={"verify_signature": False, "verify_exp": False})
        vp_token_object = VerifiablePresentationPayload.model_validate(vp_token_decoded)

        if vp_token_object.exp < datetime.now().timestamp():
            raise FACTSAuthError("VP Token expired")

        if scope == TokenScopeEnum.scope_write:
            presentation_scope = "openid tnt_write"
            presentation_id = "tnt_write_presentation"
        elif scope == TokenScopeEnum.scope_create:
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

        ebsi_token_data: EBSITokenPublic = self.auth_repository.get_token(data=authorisation_payload)

        vc_token = vp_token_object.vp.verifiableCredential[0]
        vc_token_decoded = jwt.decode(vc_token, options={"verify_signature": False, "verify_exp": False})
        vc_token_object = VerifiableCredentialPayload.model_validate(vc_token_decoded)
        credential_object = vc_token_object.vc.credentialSubject
        """
        scopes: list[str] | None = None
        credential_subject: dict | None = None
        verifiable_credential: str | None = None
        ebsi_access_token: str | None = None
        """

        user = User(ebsi_access_token=ebsi_token_data.access_token, scopes=ebsi_token_data.scope.split(" "),
                    credential_subject=credential_object, verifiable_credential=vc_token, exp="")

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