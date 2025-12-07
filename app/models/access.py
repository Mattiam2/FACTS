from sqlmodel import Field

from app.schemas.access import AccessBase


class Access(AccessBase, table=True):
    __tablename__ = "accesses"
    __table_args__ = {'schema': 'public'}

    id: str = Field(default=None, primary_key=True)
    document_id: str = Field(foreign_key="documents.id", schema_extra={'serialization_alias': 'documentId'})