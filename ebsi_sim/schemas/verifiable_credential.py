from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class CredentialSchemaPublic(SQLModel):
    id: Optional[str] = None
    type: Optional[str] = None


class CredentialSubjectPublic(SQLModel):
    id: Optional[str] = None


class VerifiableCredentialPublic(SQLModel):
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
    iss: str
    sub: str
    iat: int
    nbf: int
    exp: int
    jti: str
    vc: VerifiableCredentialPublic