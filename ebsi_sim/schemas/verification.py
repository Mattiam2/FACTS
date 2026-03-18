from datetime import datetime

from sqlmodel import SQLModel, Field


class VerificationMethodBase(SQLModel):
    id: str
    type: str
    did_controller: str = Field(schema_extra={'serialization_alias': 'controller'})
    public_key: str


class VerificationRelationshipBase(SQLModel):
    id: int
    identifier_did: str = Field(schema_extra={'serialization_alias': 'did'})
    name: str
    vmethodid: str = Field(schema_extra={'serialization_alias': 'vMethodId'})
    notbefore: datetime = Field(schema_extra={'serialization_alias': 'notBefore'})
    notafter: datetime = Field(schema_extra={'serialization_alias': 'notAfter'})
