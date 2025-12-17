from sqlmodel import SQLModel, Field

from ebsi_sim.schemas.shared import PageLinksPublic, TimestampPublic


class DocumentItemPublic(SQLModel):
    documentId: str
    href: str


class DocumentListPublic(SQLModel):
    self: str
    items: list[DocumentItemPublic]
    total: int
    pageSize: int
    links: PageLinksPublic


class DocumentPublic(SQLModel):
    metadata_text: str = Field(schema_extra={'serialization_alias': 'metadata'})
    timestamp: TimestampPublic
    creator: str