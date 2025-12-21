from sqlmodel import SQLModel, Field

from ebsi_sim.schemas.shared import PageLinksPublic, TimestampPublic


class DocumentItemPublic(SQLModel):
    """
    Represents an EBSI Document list item with metadata and hyperlink.

    :ivar documentId: Unique identifier for the document.
    :type documentId: str
    :ivar href: Hyperlink to access or reference the document.
    :type href: str
    """

    documentId: str
    href: str


class DocumentListPublic(SQLModel):
    """
    Represents a list of EBSI Document items

    This class is used to handle and structure a paginated list of document items.
    It includes the total number of items, the current page size, and the associated page links.

    :ivar self: Specifies the URI of the current resource.
    :type self: str
    :ivar items: List of public document items.
    :type items: list[DocumentItemPublic]
    :ivar total: Total number of document items available across all pages.
    :type total: int
    :ivar pageSize: Number of document items displayed per page.
    :type pageSize: int
    :ivar links: Navigation links for the paginated document list.
    :type links: PageLinksPublic
    """

    self: str
    items: list[DocumentItemPublic]
    total: int
    pageSize: int
    links: PageLinksPublic


class DocumentPublic(SQLModel):
    """
    Represents an EBSI Document with metadata and timestamp.

    This class encapsulates information pertaining to a public document, including its
    metadata text, timestamp, and the creator

    :ivar metadata_text: The metadata of the document
    :type metadata_text: str
    :ivar timestamp: The timestamp when the document was recorded.
    :type timestamp: TimestampPublic
    :ivar creator: Denotes the creator of the document.
    :type creator: str
    """

    metadata_text: str = Field(schema_extra={'serialization_alias': 'metadata'})
    timestamp: TimestampPublic
    creator: str