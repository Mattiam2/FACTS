from datetime import datetime

from sqlmodel import Field

from app.schemas.event import EventBase


class Event(EventBase, table=True):
    __tablename__ = "events"
    __table_args__ = {'schema': 'public'}

    id: str = Field(default=None, primary_key=True)
    document_id: str = Field(foreign_key="documents.id")
    timestamp_datetime: datetime
    timestamp_source: str
    timestamp_proof: str