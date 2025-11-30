from sqlmodel import SQLModel, Field

from app.schemas.shared import PageLinksPublic, TimestampPublic


class EventBase(SQLModel):
    metadata_json: str = Field(schema_extra={'serialization_alias': 'metadata'})
    sender: str
    origin: str
    hash: str
    external_hash: str


class EventItemPublic(SQLModel):
    eventId: str
    href: str


class EventListPublic(SQLModel):
    self: str
    items: list[EventItemPublic]
    total: int
    pageSize: int
    links: PageLinksPublic


class EventPublic(EventBase):
    timestamp: TimestampPublic