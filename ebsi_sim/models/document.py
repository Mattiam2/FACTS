from datetime import datetime

from sqlmodel import SQLModel, Field


class Document(SQLModel, table=True):
    """
    Represents an EBSI document model for storing and managing documents.

    It includes information such as unique identifier, metadata, timestamps,
    and creator details.

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
