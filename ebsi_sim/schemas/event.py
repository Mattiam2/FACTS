from sqlmodel import SQLModel, Field

from ebsi_sim.schemas.shared import PageLinksPublic, TimestampPublic


class EventBase(SQLModel):
    """
    Represents an EBSI event base model

    :ivar metadata_text: Metadata information for the event
    :type metadata_text: str
    :ivar sender: Identifier of the sender of the event.
    :type sender: str
    :ivar origin: Origin or source of the event.
    :type origin: str
    :ivar hash: Unique hash value representing the event.
    :type hash: str
    :ivar external_hash: External hash value associated with the event
    :type external_hash: str, optional
    """

    metadata_text: str = Field(schema_extra={'serialization_alias': 'metadata'})
    sender: str
    origin: str
    hash: str
    external_hash: str = Field(None, schema_extra={'serialization_alias': 'externalHash'})


class EventItemPublic(SQLModel):
    """
    Represents an EBSI event list item

    :ivar eventId: Unique identifier for the event.
    :type eventId: str
    :ivar href: URL of the resource representing the event.
    :type href: str
    """

    eventId: str
    href: str


class EventListPublic(SQLModel):
    """
    Represents an accessible list of events

    :ivar self: A unique resource URL for the event list.
    :type self: str
    :ivar items: A collection of event items.
    :type items: list[EventItemPublic]
    :ivar total: The total number of items in the event list.
    :type total: int
    :ivar pageSize: The number of items per page in the paginated response.
    :type pageSize: int
    :ivar links: Pagination links, such as next or previous page.
    :type links: PageLinksPublic
    """

    self: str
    items: list[EventItemPublic]
    total: int
    pageSize: int
    links: PageLinksPublic


class EventPublic(EventBase):
    """
    Represents an EBSI event schema

    :ivar timestamp: The timestamp when the event occurred
    :type timestamp: TimestampPublic
    """

    timestamp: TimestampPublic