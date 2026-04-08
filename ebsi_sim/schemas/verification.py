from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field


class VerificationMethodBase(SQLModel):
    id: str
    type: str
    did_controller: str = Field(schema_extra={'serialization_alias': 'controller'})
    public_key: str


class VerificationRelationshipNameEnum(str, Enum):
    authentication = "authentication"  # For authenticate the entity itself
    assertionMethod = "assertionMethod"  # For sign and issue a VC
    capabilityInvocation = "capabilityInvocation"
    capabilityDelegation = "capabilityDelegation"
    keyAgreement = "keyAgreement"


class VerificationRelationshipBase(SQLModel):
    id: int
    identifier_did: str = Field(schema_extra={'serialization_alias': 'did'})
    name: VerificationRelationshipNameEnum
    vmethodid: str = Field(schema_extra={'serialization_alias': 'vMethodId'})
    notbefore: datetime = Field(schema_extra={'serialization_alias': 'notBefore'})
    notafter: datetime = Field(schema_extra={'serialization_alias': 'notAfter'})
