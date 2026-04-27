from sqlmodel import SQLModel, Field

from ebsi_sim.src.schemas.shared import PageLinksPublic
from ebsi_sim.src.schemas.verification import VerificationMethodBase


class IdentifierBase(SQLModel):
    """
    Represents an EBSI Identifier base schema for storing and managing grants data.

    :ivar did: A unique record id = DID User
    :type did: str
    """
    did: str = Field(description="A unique record id = DID User")


class IdentifierPublic(IdentifierBase):
    did: str | None = Field(default=None, schema_extra={'serialization_alias': 'id'})
    controller: list[str] | None = None
    verificationMethod: list[VerificationMethodBase] | None = None
    authentication: list[str] | None = None
    assertionMethod: list[str] | None = None
    capabilityInvocation: list[str] | None = None
    capabilityDelegation: list[str] | None = None
    keyAgreement: list[str] | None = None


class IdentifierItemPublic(IdentifierBase):
    """
    Represents an EBSI Identifier list item

    :ivar href: URL of the resource representing the identifier.
    :type href: str
    """
    href: str | None = Field(default=None, description="Link to the resource")


class IdentifierListPublic(SQLModel):
    """
    Represents a list of EBSI Identifier items

    This class is used to handle and structure a paginated list of identifier items.
    It includes the total number of items, the current page size, and the associated page links.

    :ivar self: A string representing the current API endpoint.
    :type self: str
    :ivar items: A list of public identifier items.
    :type items: list[IdentifierItemPublic]
    :ivar total: The total number of items in the list.
    :type total: int
    :ivar page_size: The number of items per page in the current list.
    :type page_size: int
    :ivar links: An instance of PageLinksPublic containing links for pagination and navigation.
    :type links: PageLinksPublic
    """

    self: str | None = Field(default=None, description="Filter by controller DID.")
    items: list[IdentifierItemPublic] | None = Field(default=None, description="List of identifier.")
    total: int | None = Field(default=None, description="Total number of items across all pages.")
    page_size: int | None = Field(default=None, schema_extra={'serialization_alias': 'pageSize'},
                           description="Maximum number of items per page. For the last page, its value should be independent of the number of actually returned items.")
    links: PageLinksPublic | None = Field(default=None, description="Links model used for pagination")
