from dataclasses import dataclass

from sqlmodel import SQLModel, Field
from typing_extensions import TypedDict

from src.schemas.shared import TimestampPublic, PageLinksPublic


class EventBase(SQLModel):
    """
    Represents an EBSI event base model

    :ivar metadata_text: Metadata information for the event
    :type metadata_text: str
    :ivar sender: Identifier of the sender of the event.
    :type sender: str
    :ivar origin: Origin or source of the event.
    :type origin: str
    :ivar id: Unique hash value representing the event.
    :type id: str
    :ivar external_hash: External hash value associated with the event
    :type external_hash: str, optional
    """

    metadata_text: str = Field(schema_extra={'serialization_alias': 'metadata'}, description="Event's metadata")
    sender: str = Field(description="The `did:key` or `did:ebsi` that created the event")
    origin: str = Field(
        description="Most of the times empty field, while it may be a string containing company name, while it can also point into an Event. All assumed relations are external to the SC.")
    id: str = Field(schema_extra={'serialization_alias': 'hash'}, description="Event hash")
    external_hash: str | None = Field(None, schema_extra={'serialization_alias': 'externalHash'},
                                      description="Externally generated hash")


class EventItemPublic(SQLModel):
    """
    Represents an EBSI event list item

    :ivar event_id: Unique identifier for the event.
    :type event_id: str
    :ivar href: URL of the resource representing the event.
    :type href: str
    """

    event_id: str = Field(schema_extra={'serialization_alias': 'eventId'}, description="Event ID")
    href: str = Field(description="Link to the resource")


class EventListPublic(SQLModel):
    """
    Represents an accessible list of events

    :ivar self: A unique resource URL for the event list.
    :type self: str
    :ivar items: A collection of event items.
    :type items: list[EventItemPublic]
    :ivar total: The total number of items in the event list.
    :type total: int
    :ivar page_size: The number of items per page in the paginated response.
    :type page_size: int
    :ivar links: Pagination links, such as next or previous page.
    :type links: PageLinksPublic
    """

    self: str = Field(description="Absolute path to the collection (consult)")
    items: list[EventItemPublic] = Field(description="List of events")
    total: int = Field(description="Total number of items across all pages.")
    page_size: int = Field(schema_extra={'serialization_alias': 'pageSize'},
                           description="Maximum number of items per page. For the last page, its value should be independent of the number of actually returned items.")
    links: PageLinksPublic = Field(description="Links model used for pagination")


class EventPublic(EventBase):
    """
    Represents an EBSI event schema

    :ivar timestamp: The timestamp when the event occurred
    :type timestamp: TimestampPublic
    """

    timestamp: TimestampPublic = Field(description="Timestamp object")


@dataclass
class EventParams(TypedDict):
    """
    Represents the parameters for an event.

    :ivar documentHash: The hash of the associated document. This could be in bytes or
        string format.
    :type documentHash: bytes | str
    :ivar externalHash: An external generated hash of the event.
    :type externalHash: str
    :ivar sender: The sender's did. This could be in bytes or string format.
    :type sender: bytes | str
    :ivar origin: The origin of the event in string format.
    :type origin: str
    :ivar metadata: Additional metadata associated with the event in string format.
    :type metadata: str
    """
    documentHash: bytes | str
    externalHash: str
    sender: bytes | str
    origin: str
    metadata: str
