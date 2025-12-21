from sqlmodel import SQLModel, Field

from ebsi_sim.schemas.shared import PermissionEnum, PageLinksPublic


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
    subject: str
    granted_by: str = Field(schema_extra={'serialization_alias': 'grantedBy'})
    permission: PermissionEnum


class AccessItemPublic(AccessBase):
    """
    Represents an EBSI Access list item

    :ivar document_id: Identifier for the associated document.
    :type document_id: str
    """
    document_id: str = Field(schema_extra={'serialization_alias': 'documentId'})


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
    :ivar pageSize: The number of items per page in the current list.
    :type pageSize: int
    :ivar links: An instance of PageLinksPublic containing links for pagination and navigation.
    :type links: PageLinksPublic
    """

    self: str
    items: list[AccessItemPublic]
    total: int
    pageSize: int
    links: PageLinksPublic