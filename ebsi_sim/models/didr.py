from datetime import datetime

from sqlmodel import SQLModel, Field

from ebsi_sim.schemas.identifier import IdentifierBase
from ebsi_sim.schemas.verification import VerificationMethodBase, VerificationRelationshipBase


class VerificationMethod(VerificationMethodBase, table=True):
    __tablename__ = "verification_methods"
    __table_args__ = {'schema': 'public'}

    id: str = Field(primary_key=True)
    did_controller: str = Field(foreign_key="public.identifiers.did", schema_extra={'serialization_alias': 'controller'})
    issecp256k1: bool
    notafter: datetime

class VerificationRelationship(VerificationRelationshipBase, table=True):
    __tablename__ = "verification_relationships"
    __table_args__ = {'schema': 'public'}

    id: int = Field(primary_key=True, default=None)
    identifier_did: str = Field(foreign_key="public.identifiers.did", schema_extra={'serialization_alias': 'did'})
    vmethodid: str = Field(foreign_key="public.verification_methods.id", schema_extra={'serialization_alias': 'vMethodId'})


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
