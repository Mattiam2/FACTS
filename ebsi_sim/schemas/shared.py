from enum import Enum

from sqlmodel import SQLModel


class TimestampPublic(SQLModel):
    """
    Represents a public timestamp model.

    This class models a timestamp object containing the datetime of creation,
    the source of the timestamp, and a proof of its existence.

    :ivar datetime: The date and time of the timestamp creation.
    :type datetime: str
    :ivar source: The origin or reference source of the timestamp.
    :type source: str
    :ivar proof: The evidence or verification data associated with the timestamp.
    :type proof: str
    """

    datetime: str
    source: str
    proof: str


class PageLinksPublic(SQLModel):
    """
    Represents public pagination links.

    :ivar first: The URL of the first page.
    :type first: str
    :ivar prev: The URL of the previous page.
    :type prev: str
    :ivar next: The URL of the next page.
    :type next: str
    :ivar last: The URL of the last page.
    :type last: str
    """

    first: str
    prev: str
    next: str
    last: str


class VersionEnum(str, Enum):
    """
    Enumeration of versions.
    """

    latest = "latest"
    deprecated = "deprecated"


class PermissionEnum(str, Enum):
    """
    Represents an enumeration of permissions.

    :ivar write: Represents the permission to write.
    :type write: str
    :ivar delegate: Represents the permission to delegate access.
    :type delegate: str
    :ivar creator: Represents the permission of being a creator.
    :type creator: str
    """

    write = "write"
    delegate = "delegate"
    creator = "creator"