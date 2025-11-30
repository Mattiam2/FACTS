from enum import Enum

from sqlmodel import SQLModel


class TimestampPublic(SQLModel):
    datetime: str
    source: str
    proof: str


class PageLinksPublic(SQLModel):
    first: str
    prev: str
    next: str
    last: str


class VersionEnum(str, Enum):
    latest = "latest"
    deprecated = "deprecated"


class PermissionEnum(str, Enum):
    write = "write"
    delegate = "delegate"
    creator = "creator"