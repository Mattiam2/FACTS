from datetime import datetime

from sqlmodel import Field, Relationship

from ebsi_sim.schemas.access import AccessBase
from ebsi_sim.schemas.document import DocumentBase
from ebsi_sim.schemas.event import EventBase


class Access(AccessBase, table=True):
    """
    Represents an EBSI Access model for storing and managing grants data.

    :ivar id: Unique identifier for the access record.
    :type id: int
    :ivar document_id: Identifier of the associated document.
    :type document_id: str
    """

    __tablename__ = "accesses"
    __table_args__ = {'schema': 'public'}

    id: int = Field(primary_key=True, nullable=False)
    document_id: str = Field(foreign_key="public.documents.id", schema_extra={'serialization_alias': 'documentId'})

    document: "Document" = Relationship(back_populates="accesses")


class Document(DocumentBase, table=True):
    """
    Represents an EBSI Document model for storing and managing documents.

    :ivar id: The unique identifier for the document.
    :type id: str
    :ivar metadata_text: The metadata of the document.
    :type metadata_text: str
    :ivar timestamp_datetime: The date and time when the document was
        created or recorded.
    :type timestamp_datetime: datetime
    :ivar timestamp_source: The source information for the timestamp,
        indicating how or where it was derived.
    :type timestamp_source: str
    :ivar timestamp_proof: Evidence or proof supporting the validity of the
        timestamp.
    :type timestamp_proof: str
    :ivar creator: The creator of the document.
    :type creator: str
    """

    __tablename__ = "documents"
    __table_args__ = {'schema': 'public'}

    id: str = Field(default=None, primary_key=True)
    metadata_text: str = Field(schema_extra={'serialization_alias': 'metadata'})
    timestamp_datetime: datetime
    timestamp_source: str
    timestamp_proof: str
    creator: str

    events: list["Event"] = Relationship(back_populates="document")
    accesses: list["Access"] = Relationship(back_populates="document")


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

    document: Document = Relationship(back_populates="events")