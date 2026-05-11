from sqlmodel import SQLModel, Field


class CredentialSubject(SQLModel):
    subject_did: str
    company_name: str
    company_address: str
    company_vat: str
    company_website: str
    company_email: str
    company_country: str


class PublisherSubject(CredentialSubject):
    authorized_hosts: list[str]


class FactCheckerSubject(CredentialSubject):
    specialization: str | None
    accredited_by: str | None


class CredentialCreate(SQLModel):
    """
    Represents the schema for a request of a verifiable credential.

    :ivar subject_did: DID Subject of the request.
    :type subject_did: str
    :ivar credential_type: Credential type(s), which can be a list of strings.
    :type credential_type: list[str] | None
    :ivar credential_subject: Credential subject, represented as a dictionary with
        string keys and values.
    :type credential_subject: dict[str, str] | None
    """
    subject_did: str = Field(description="DID Subject of the request")
    credential_type: list[str] | str | None = Field(default=None, description="Credential type(s)")
    credential_subject: dict[str, str | list[str]] | None = Field(default=None, description="Credential subject")
