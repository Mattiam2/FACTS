from sqlmodel import SQLModel, Field

from ebsi_sim.schemas.presentation import ScopeEnum


class TokenCreate(SQLModel):
    grant_type: str
    vp_token: str
    presentation_definition: str
    scope: ScopeEnum


class TokenBase(SQLModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: ScopeEnum
    id_token: str = Field(regex=r'^(([A-Za-z0-9\-_])+\.)([A-Za-z0-9\-_]+)(\.([A-Za-z0-9\-_]+)?$')