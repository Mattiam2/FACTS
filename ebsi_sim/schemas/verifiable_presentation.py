from sqlmodel import SQLModel, Field


class VerifiablePresentationPublic(SQLModel):
    context: list[str] = Field(default_factory=list, alias="@context")
    id: str
    type: list[str] = Field(default_factory=list)
    holder: str
    verifiableCredential: list[str] = Field(default_factory=list)


class VerifiablePresentationPayload(SQLModel):
    iss: str
    aud: str
    sub: str
    iat: int
    nbf: int
    exp: int
    nonce: str
    jti: str
    vp: VerifiablePresentationPublic
