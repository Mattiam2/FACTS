from sqlmodel import SQLModel, Field

from schemas.shared import TimestampPublic, PageLinksPublic


class DocumentItemPublic(SQLModel):
    """
    Represents an EBSI Document list item with metadata and hyperlink.

    :ivar document_id: Unique identifier for the document.
    :type document_id: str
    :ivar href: Hyperlink to access or reference the document.
    :type href: str
    """

    document_id: str = Field(schema_extra={'serialization_alias': 'documentId'}, description="Document ID")
    href: str = Field(description="Link to the resource")


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
    :ivar page_size: Number of document items displayed per page.
    :type page_size: int
    :ivar links: Navigation links for the paginated document list.
    :type links: PageLinksPublic
    """

    self: str = Field(description="Absolute path to the collection (consult)")
    items: list[DocumentItemPublic] = Field(description="List of documents")
    total: int = Field(description="Total number of items across all pages.")
    page_size: int = Field(schema_extra={'serialization_alias': 'pageSize'},
                           description="Maximum number of items per page. For the last page, its value should be independent of the number of actually returned items.")
    links: PageLinksPublic = Field(description="Links model used for pagination")


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

    metadata_text: str = Field(schema_extra={'serialization_alias': 'metadata'}, description="Document's metadata")
    timestamp: TimestampPublic = Field(description="Document's metadata")
    creator: str = Field(description="The `did:key` or `did:ebsi` that created the document")
