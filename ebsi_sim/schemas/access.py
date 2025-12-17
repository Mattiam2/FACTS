from sqlmodel import SQLModel, Field

from ebsi_sim.schemas.shared import PermissionEnum, PageLinksPublic


class AccessBase(SQLModel):
    subject: str
    granted_by: str = Field(schema_extra={'serialization_alias': 'grantedBy'})
    permission: PermissionEnum


class AccessItemPublic(AccessBase):
    document_id: str = Field(schema_extra={'serialization_alias': 'documentId'})


class AccessListPublic(SQLModel):
    self: str
    items: list[AccessItemPublic]
    total: int
    pageSize: int
    links: PageLinksPublic