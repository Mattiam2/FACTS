from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field


class VerificationMethodBase(SQLModel):
    """
    Represents a base schema for verification methods used in systems requiring
    identity validation.

    :ivar id: Unique identifier for the verification method.
    :type id: str
    :ivar type: Type or category of the verification method.
    :type type: str
    :ivar did_controller: Associated DID controller, identifying the controlling
        entity of the verification method.
    :type did_controller: str
    :ivar public_key: Public key used in the verification process.
    :type public_key: str
    """
    id: str
    type: str
    did_controller: str = Field(schema_extra={'serialization_alias': 'controller'})
    public_key: str


class VerificationRelationshipNameEnum(str, Enum):
    """
    Enumeration of verification relationship names.
    """
    authentication = "authentication"  # For authenticate the entity itself
    assertionMethod = "assertionMethod"  # For sign and issue a VC
    capabilityInvocation = "capabilityInvocation"
    capabilityDelegation = "capabilityDelegation"
    keyAgreement = "keyAgreement"


class VerificationRelationshipBase(SQLModel):
    """
    Represents the base schema for a verification relationship.

    :ivar id: The unique identifier of the verification relationship.
    :type id: int
    :ivar identifier_did: The decentralized identifier (DID) associated with the
        verification relationship.
    :type identifier_did: str
    :ivar name: The name of the verification relationship, represented as an
        enumerated value.
    :type name: VerificationRelationshipNameEnum
    :ivar vmethodid: The verification method identifier associated with this
        relationship.
    :type vmethodid: str
    :ivar notbefore: The timestamp before which the verification relationship is
        not considered valid.
    :type notbefore: datetime
    :ivar notafter: The timestamp after which the verification relationship is no
        longer considered valid.
    :type notafter: datetime
    """
    id: int
    identifier_did: str = Field(schema_extra={'serialization_alias': 'did'})
    name: VerificationRelationshipNameEnum
    vmethodid: str = Field(schema_extra={'serialization_alias': 'vMethodId'})
    notbefore: datetime = Field(schema_extra={'serialization_alias': 'notBefore'})
    notafter: datetime = Field(schema_extra={'serialization_alias': 'notAfter'})
