from datetime import datetime

from sqlmodel import SQLModel, Field


class Document(SQLModel, table=True):
    __tablename__ = "documents"
    __table_args__ = {'schema': 'public'}

    id: str = Field(default=None, primary_key=True)
    metadata_json: str = Field(schema_extra={'serialization_alias': 'metadata'})
    timestamp_datetime: datetime
    timestamp_source: str
    timestamp_proof: str
    creator: str
