from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field

from ebsi_sim.schemas.presentation import ScopeEnum


class GrantTypeEnum(str, Enum):
    vp_token = "vp_token"


class PresentationDescriptor(SQLModel):
    id: str
    format: str
    path: str
    path_nested: Optional["PresentationDescriptor"] = None


class PresentationSubmission(SQLModel):
    id: str
    definition_id: str
    descriptor_map: list[PresentationDescriptor]


class TokenCreate(SQLModel):
    grant_type: GrantTypeEnum = Field(description="MUST be set to `vp_token`")
    vp_token: str = Field(description="The Verifiable Presentation Token")
    presentation_submission: PresentationSubmission = Field(
        description="Descriptor for the vp_token, linked by presentation_definition.")
    scope: ScopeEnum = Field(description="OIDC scope")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "grant_type": "vp_token",
                    "vp_token": "string",
                    "presentation_submission": {
                        "definition_id": "didr_invite_presentation",
                        "descriptor_map": [
                            {
                                "format": "jwt_vp",
                                "id": "didr_invite_credential",
                                "path": "$",
                                "path_nested": {
                                    "format": "jwt_vc",
                                    "id": "didr_invite_credential",
                                    "path": "$.vp.verifiableCredential[0]"
                                }
                            }
                        ],
                        "id": "ac9026c2-c3f5-4a26-b609-ec215cf97ba2"
                    },
                    "scope": "openid didr_invite"
                }
            ]
        }
    }


class TokenTypeEnum(str, Enum):
    bearer = "Bearer"


class TokenBase(SQLModel):
    access_token: str = Field(description="The access token issued by the Authorisation Server in JWS format.")
    token_type: TokenTypeEnum = Field(description="MUST be `Bearer`")
    expires_in: int = Field(description="The lifetime in seconds of the access token.", ge=1)
    scope: ScopeEnum = Field(description="The scope of the access token")
    id_token: str = Field(
        description="ID Token value associated with the authenticated session. Presents client's identity. ID Token is issued in a JWS format.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "jwt",
                    "id_token": "jwt",
                    "token_type": "Bearer",
                    "scope": "openid tir_write",
                    "expires_in": 7200
                }
            ]
        }
    }
