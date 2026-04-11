from sqlmodel import SQLModel, Field


class VerifiablePresentationPublic(SQLModel):
    """
    Represents a verifiable presentation.

    :ivar context: Context(s) related to this verifiable presentation.
    :type context: list[str]
    :ivar id: The unique identifier for the verifiable presentation.
    :type id: str
    :ivar type: Type(s) of the verifiable presentation.
    :type type: list[str]
    :ivar holder: DID of the entity holding the verifiable presentation.
    :type holder: str
    :ivar verifiableCredential: A list of verifiable credentials contained within
        the presentation.
    :type verifiableCredential: list[str]
    """
    context: list[str] = Field(default_factory=list, alias="@context")
    id: str
    type: list[str] = Field(default_factory=list)
    holder: str
    verifiableCredential: list[str] = Field(default_factory=list)


class VerifiablePresentationPayload(SQLModel):
    """
    Represents the payload container of a verifiable presentation.

    :ivar iss: Issuer of the verifiable presentation.
    :type iss: str
    :ivar aud: Audience for which the verifiable presentation is intended.
    :type aud: str
    :ivar sub: Subject associated with the verifiable presentation.
    :type sub: str
    :ivar iat: Issued-at timestamp indicating when the payload was created.
    :type iat: int
    :ivar nbf: Not-before timestamp indicating when the payload becomes valid.
    :type nbf: int
    :ivar exp: Expiration timestamp indicating when the payload will no
        longer be valid.
    :type exp: int
    :ivar nonce: Unique nonce used to prevent replay attacks.
    :type nonce: str
    :ivar jti: Unique identifier for the payload.
    :type jti: str
    :ivar vp: Verifiable presentation.
    :type vp: VerifiablePresentationPublic
    """
    iss: str
    aud: str
    sub: str
    iat: int
    nbf: int
    exp: int
    nonce: str
    jti: str
    vp: VerifiablePresentationPublic
