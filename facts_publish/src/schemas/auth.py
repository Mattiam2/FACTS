from enum import Enum

from sqlmodel import SQLModel, Field


class TokenRequestScopeEnum(str, Enum):
    scope_create = "create"
    scope_write = "write"

class TokenResponseScopeEnum(str, Enum):
    didr_write = "openid didr_write"
    didr_invite = "openid didr_invite"
    tir_write = "openid tir_write"
    tir_invite = "openid tir_invite"
    timestamp_write = "openid timestamp_write"
    tnt_authorise = "openid tnt_authorise"
    tnt_create = "openid tnt_create"
    tnt_write = "openid tnt_write"
    tpr_write = "openid tpr_write"
    tsr_write = "openid tsr_write"

class TokenCreate(SQLModel):
    vp_token: str
    scope: TokenRequestScopeEnum

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
    scope: TokenResponseScopeEnum | None = Field(default=None, description="The scope of the access token")
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
