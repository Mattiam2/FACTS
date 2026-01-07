from datetime import datetime

from sqlmodel import Field

from ebsi_sim.schemas.event import EventBase


class Event(EventBase, table=True):
    """
    Represents an EBSI Event model for storing and managing events.

    :ivar id: Unique identifier for the event.
    :ivar document_id: Identifier for the associated document.
    :ivar timestamp_datetime: The datetime when the event occurred.
    :ivar timestamp_source: The source from which the timestamp was obtained.
    :ivar timestamp_proof: Evidence or proof supporting the event's timestamp.
    """

    __tablename__ = "events"
    __table_args__ = {'schema': 'public'}

    id: str = Field(default=None, primary_key=True)
    document_id: str = Field(foreign_key="public.documents.id")
    timestamp_datetime: datetime
    timestamp_source: str
    timestamp_proof: str