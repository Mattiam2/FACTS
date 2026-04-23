from enum import Enum

from sqlmodel import SQLModel, Field


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

    datetime: str | None = Field(None, description="The date and time, optionally from transaction input")
    source: str | None = Field(None,
                               description="Defines how the datetime was resolved, enumerated options are 'block' and 'external'")
    proof: str | None = Field(None,
                              description="Proof of the source. Either a block number or a hash of timestamp certificate")


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

    first: str = Field(description="URI of the first page")
    prev: str = Field(description="URI of the previous page")
    next: str = Field(description="URI of the next page")
    last: str = Field(description="URI of the last page")


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
    :ivar creator: If document is created by the creator
    :type creator: str
    """

    write = "write"
    delegate = "delegate"
    creator = "creator"
