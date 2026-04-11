from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class CredentialSchemaPublic(SQLModel):
    id: Optional[str] = None
    type: Optional[str] = None


class CredentialSubjectPublic(SQLModel):
    id: Optional[str] = None


class VerifiableCredentialPublic(SQLModel):
    """
    Represents a Verifiable Credential

    :ivar context: Context(s) related to this verifiable credential.
    :type context: list[str]
    :ivar id: Unique identifier of the verifiable credential.
    :type id: str
    :ivar type: Type(s) of the verifiable credential
    :type type: list[str]
    :ivar issuanceDate: The date and time when the credential was issued.
    :type issuanceDate: Optional[datetime]
    :ivar validFrom: The date and time when the credential becomes valid.
    :type validFrom: Optional[datetime]
    :ivar validUntil: The date and time when the credential is no longer valid.
    :type validUntil: Optional[datetime]
    :ivar expirationDate: The date and time when the credential expires.
    :type expirationDate: Optional[datetime]
    :ivar issued: The date and time when the issuer issued the credential.
    :type issued: Optional[datetime]
    :ivar issuer: DID of the authority that issued the credential.
    :type issuer: Optional[str]
    :ivar credentialSubject: The subject of the credential
    :type credentialSubject: CredentialSubjectPublic
    :ivar credentialSchema: The schema used to define the structure of the credential.
    :type credentialSchema: CredentialSchemaPublic
    """
    context: list[str] = Field(default_factory=list, alias="@context")
    id: str
    type: list[str] = Field(default_factory=list)
    issuanceDate: Optional[datetime] = None
    validFrom: Optional[datetime] = None
    validUntil: Optional[datetime] = None
    expirationDate: Optional[datetime] = None
    issued: Optional[datetime] = None
    issuer: Optional[str] = None
    credentialSubject: CredentialSubjectPublic
    credentialSchema: CredentialSchemaPublic


class VerifiableCredentialPayload(SQLModel):
    """
    Represents the payload container of a verifiable credential.

    :ivar iss: The issuer of the verifiable credential.
    :type iss: str
    :ivar sub: The subject of the verifiable credential.
    :type sub: str
    :ivar iat: The issuance timestamp of the verifiable credential
        in seconds since the Unix epoch.
    :type iat: int
    :ivar nbf: The "not before" timestamp, indicating the time before
        which the credential is not valid, in seconds since the Unix epoch.
    :type nbf: int
    :ivar exp: The expiration timestamp of the verifiable credential
        in seconds since the Unix epoch.
    :type exp: int
    :ivar jti: The unique identifier (JWT ID) of the verifiable credential.
    :type jti: str
    :ivar vc: The verifiable credential
    :type vc: VerifiableCredentialPublic
    """
    iss: str
    sub: str
    iat: int
    nbf: int
    exp: int
    jti: str
    vc: VerifiableCredentialPublic
