from sqlmodel import SQLModel, Field

from ebsi_sim.schemas.shared import PageLinksPublic
from ebsi_sim.schemas.verification_method import VerificationMethodBase


class IdentifierBase(SQLModel):
    """
    Represents an EBSI Identifier base schema for storing and managing grants data.

    :ivar did: A unique record id = DID User
    :type did: str
    """
    did: str

class IdentifierPublic(IdentifierBase):

    did: str = Field(schema_extra={'serialization_alias': 'id'})
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
    href: str


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
    :ivar pageSize: The number of items per page in the current list.
    :type pageSize: int
    :ivar links: An instance of PageLinksPublic containing links for pagination and navigation.
    :type links: PageLinksPublic
    """

    self: str
    items: list[IdentifierItemPublic]
    total: int
    pageSize: int
    links: PageLinksPublic