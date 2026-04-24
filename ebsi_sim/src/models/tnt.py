from datetime import datetime

from sqlmodel import Field, Relationship, func, SQLModel

from models.didr import Identifier
from schemas.access import AccessItemPublic
from schemas.event import EventBase


class Access(AccessItemPublic, table=True):
    """
    Represents an EBSI Access model for storing and managing grants data.

    :ivar id: Unique identifier for the access record.
    :type id: int
    :ivar document_id: Identifier of the associated document.
    :type document_id: str
    :ivar document: The associated document entity.
    :type document: Document
    """

    __tablename__ = "accesses"
    __table_args__ = {'schema': 'public'}

    id: int = Field(primary_key=True, nullable=False)
    document_id: str = Field(foreign_key="public.documents.id", schema_extra={'serialization_alias': 'documentId'})
    subject: str = Field(foreign_key="public.identifiers.did", description="Subject")
    granted_by: str = Field(foreign_key="public.identifiers.did", schema_extra={'serialization_alias': 'grantedBy'},
                            description="DID that granted the access")

    document: "Document" = Relationship(back_populates="accesses")
    subject_identifier: "Identifier" = Relationship(sa_relationship_kwargs={"foreign_keys": "Access.subject"})
    granted_by_identifier: "Identifier" = Relationship(sa_relationship_kwargs={"foreign_keys": "Access.granted_by"})


class Document(SQLModel, table=True):
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
    :ivar events: A list of associated event entities with the document.
    :type events: list[Event]
    :ivar accesses: A list of associated access entities with the document.
    :type accesses: list[Access]
    """

    __tablename__ = "documents"
    __table_args__ = {'schema': 'public'}

    id: str = Field(default=None, primary_key=True)
    metadata_text: str = Field(schema_extra={'serialization_alias': 'metadata'})
    timestamp_datetime: datetime = Field(default=func.now())
    timestamp_source: str
    timestamp_proof: str | None
    creator: str = Field(foreign_key="public.identifiers.did")

    events: list["Event"] = Relationship(back_populates="document")
    accesses: list["Access"] = Relationship(back_populates="document")
    creator_identifier: "Identifier" = Relationship()


class Event(EventBase, table=True):
    """
    Represents an EBSI Event model for storing and managing events.

    :ivar id: Unique identifier for the event.
    :type id: str
    :ivar document_id: Identifier for the associated document.
    :type document_id: str
    :ivar timestamp_datetime: The datetime when the event occurred.
    :type timestamp_datetime: datetime
    :ivar timestamp_source: The source from which the timestamp was obtained.
    :type timestamp_source: str
    :ivar timestamp_proof: Evidence or proof supporting the event's timestamp.
    :type timestamp_proof: str
    :ivar document: The associated document entity.
    :type document: Document
    """

    __tablename__ = "events"
    __table_args__ = {'schema': 'public'}

    id: str = Field(schema_extra={'serialization_alias': 'hash'}, primary_key=True)
    document_id: str = Field(foreign_key="public.documents.id")
    sender: str = Field(foreign_key="public.identifiers.did", description="The `did:key` or `did:ebsi` that created the event")
    timestamp_datetime: datetime = Field(default=func.now())
    timestamp_source: str
    timestamp_proof: str | None

    sender_identifier: Identifier = Relationship()
    document: Document = Relationship(back_populates="events")
