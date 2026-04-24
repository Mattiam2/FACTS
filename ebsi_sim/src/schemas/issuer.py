from sqlmodel import SQLModel, Field


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
    credential_subject: dict[str, str] | None = Field(default=None, description="Credential subject")