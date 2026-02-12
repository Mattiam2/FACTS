from datetime import datetime

from sqlmodel import Field, SQLModel

from ebsi_sim.schemas.identifier import IdentifierBase

class Identifier(IdentifierBase, table=True):
    """
    Represents an EBSI Identifier model for storing and managing identifiers.

    :ivar did: Unique identifier.
    :type id: str
    :ivar created_at: Datetime when the identifier was created.
    :type created_at: datetime
    """

    __tablename__ = "identifiers"
    __table_args__ = {'schema': 'public'}

    did: str = Field(primary_key=True)
    context: str | None = Field(default=None)
    created_at: datetime

class IdentifierController(SQLModel, table=True):
    __tablename__ = "identifier_controllers"
    __table_args__ = {'schema': 'public'}

    id: int = Field(primary_key=True, default=None)
    identifier_did: str = Field(primary_key=True, foreign_key="public.identifiers.did")
    did_controller: str = Field(primary_key=True, foreign_key="public.identifiers.did")

