from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field

from ebsi_sim.src.schemas.presentation import ScopeEnum


class GrantTypeEnum(str, Enum):
    """
    Enumeration of grant types used for defining specific authorization mechanisms.
    """
    vp_token = "vp_token"


class PresentationDescriptor(SQLModel):
    """
    Represents a descriptor for a verifiable presentation (VP).

    :ivar id: The unique identifier of the presentation.
    :type id: str
    :ivar format: The format of the presentation (e.g., PDF, PPT).
    :type format: str
    :ivar path: The storage path of the presentation file.
    :type path: str
    :ivar path_nested: (Optional) A nested PresentationDescriptor instance,
        allowing hierarchical representation of presentations.
    :type path_nested: Optional[PresentationDescriptor]
    """
    id: str
    format: str
    path: str
    path_nested: Optional["PresentationDescriptor"] = None


class PresentationSubmission(SQLModel):
    """
    Representation of a Presentation Submission.

    :ivar id: Unique identifier for the presentation submission.
    :type id: str
    :ivar definition_id: Identifier for the presentation definition associated with
        this submission.
    :type definition_id: str
    :ivar descriptor_map: List of presentation descriptors associated with this
        submission.
    :type descriptor_map: list[PresentationDescriptor]
    """
    id: str
    definition_id: str
    descriptor_map: list[PresentationDescriptor]


class TokenCreate(SQLModel):
    """
    Represents a request payload for creating a token using the `vp_token` grant type.

    This schema is designed for handling OpenID Connect token requests that involve
    Verifiable Presentations. It includes attributes to specify the grant type,
    the Verifiable Presentation Token itself, a descriptor for the token, and the
    scope of the OpenID Connect flow.

    :ivar grant_type: MUST be set to `vp_token`.
    :type grant_type: GrantTypeEnum
    :ivar vp_token: The Verifiable Presentation Token.
    :type vp_token: str
    :ivar presentation_submission: Descriptor for the `vp_token`, linked by
        `presentation_definition`.
    :type presentation_submission: PresentationSubmission
    :ivar scope: OIDC scope.
    :type scope: ScopeEnum
    """
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
    """
    Enumeration of token types.
    """
    bearer = "Bearer"


class TokenPublic(SQLModel):
    """
    Represents a response schema for token information.

    :ivar access_token: The access token issued by the Authorization Server
        in JWS format.
    :type access_token: str
    :ivar token_type: MUST be `Bearer`. Represents the type of the token.
    :type token_type: TokenTypeEnum
    :ivar expires_in: The lifetime in seconds of the access token. Must
        be greater than or equal to 1.
    :type expires_in: int
    :ivar scope: The scope of the access token.
    :type scope: ScopeEnum
    :ivar id_token: ID Token value associated with the authenticated session.
        Presents the client's identity. ID Token is issued in JWS format.
    :type id_token: str
    """
    access_token: str | None = Field(default=None, description="The access token issued by the Authorisation Server in JWS format.")
    token_type: TokenTypeEnum | None = Field(default=None, description="MUST be `Bearer`")
    expires_in: int | None = Field(default=None, description="The lifetime in seconds of the access token.", ge=1)
    scope: ScopeEnum | None = Field(default=None, description="The scope of the access token")
    id_token: str | None = Field(default=None, description="ID Token value associated with the authenticated session. Presents client's identity. ID Token is issued in a JWS format.")

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
