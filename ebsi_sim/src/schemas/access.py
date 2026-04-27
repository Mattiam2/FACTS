from sqlmodel import SQLModel, Field

from ebsi_sim.src.schemas.shared import PermissionEnum, PageLinksPublic


class AccessBase(SQLModel):
    """
    Represents an EBSI Access base schema for storing and managing grants data.

    :ivar subject: The identifier for the subject to whom access is granted.
    :type subject: str
    :ivar granted_by: The identifier for the entity or person who granted the
                      permission.
    :type granted_by: str
    :ivar permission: Defines the type of permission granted. This uses
                      the ``PermissionEnum`` enumeration to standardize
                      permission levels.
    :type permission: PermissionEnum
    """
    subject: str = Field(description="Subject")
    granted_by: str = Field(schema_extra={'serialization_alias': 'grantedBy'},
                            description="DID that granted the access")
    permission: PermissionEnum = Field(description="Type of permission")


class AccessItemPublic(AccessBase):
    """
    Represents an EBSI Access list item

    :ivar document_id: Identifier for the associated document.
    :type document_id: str
    """
    subject: str | None = Field(default=None, description="Subject")
    granted_by: str | None = Field(default=None, schema_extra={'serialization_alias': 'grantedBy'},
                            description="DID that granted the access")
    permission: PermissionEnum | None = Field(default=None, description="Type of permission")
    document_id: str | None = Field(default=None, schema_extra={'serialization_alias': 'documentId'}, description="Document ID")


class AccessListPublic(SQLModel):
    """
    Represents a list of EBSI Access items

    This class is used to handle and structure a paginated list of access items.
    It includes the total number of items, the current page size, and the associated page links.

    :ivar self: A string representing the current API endpoint.
    :type self: str
    :ivar items: A list of public access items.
    :type items: list[AccessItemPublic]
    :ivar total: The total number of items in the list.
    :type total: int
    :ivar page_size: The number of items per page in the current list.
    :type page_size: int
    :ivar links: An instance of PageLinksPublic containing links for pagination and navigation.
    :type links: PageLinksPublic
    """

    self: str | None = Field(default=None, description="Absolute path to the collection (consult)")
    items: list[AccessItemPublic] | None = Field(default=None, description="List of accesses")
    total: int | None = Field(default=None, description="Total number of items across all pages.")
    page_size: int | None = Field(default=None, schema_extra={'serialization_alias': 'pageSize'},
                           description="Maximum number of items per page. For the last page, its value should be independent of the number of actually returned items.")
    links: PageLinksPublic | None = Field(default=None, description="Links model used for pagination")
