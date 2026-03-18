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
    grant_type: GrantTypeEnum
    vp_token: str
    presentation_submission: PresentationSubmission
    scope: ScopeEnum


class TokenBase(SQLModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: ScopeEnum
    id_token: str = Field(regex=r'^(([A-Za-z0-9\-_])+\.)([A-Za-z0-9\-_]+)(\.([A-Za-z0-9\-_]+)?$')
