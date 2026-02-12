from datetime import datetime
from sqlmodel import Field, SQLModel

from ebsi_sim.schemas.verification_method import VerificationMethodBase, VerificationRelationshipBase


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