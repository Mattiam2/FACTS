from sqlmodel import SQLModel

from app.schemas.shared import PermissionEnum, PageLinksPublic


class AccessBase(SQLModel):
    subject: str
    grantedBy: str
    permission: PermissionEnum


class AccessItemPublic(AccessBase):
    documentId: str


class AccessListPublic(SQLModel):
    self: str
    items: list[AccessItemPublic]
    total: int
    pageSize: int
    links: PageLinksPublic