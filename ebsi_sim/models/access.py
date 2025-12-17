from sqlalchemy import Identity
from sqlmodel import Field

from ebsi_sim.schemas.access import AccessBase

class Access(AccessBase, table=True):
    __tablename__ = "accesses"
    __table_args__ = {'schema': 'public'}

    id: int = Field(primary_key=True, nullable=False)
    document_id: str = Field(foreign_key="public.documents.id", schema_extra={'serialization_alias': 'documentId'})