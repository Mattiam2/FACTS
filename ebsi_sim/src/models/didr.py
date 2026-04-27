from datetime import datetime

from sqlmodel import SQLModel, Field, func, Relationship

from ebsi_sim.src.schemas.identifier import IdentifierBase
from ebsi_sim.src.schemas.verification import VerificationMethodBase, VerificationRelationshipBase


class VerificationMethod(VerificationMethodBase, table=True):
    """
    Represents a verification method table model.

    :ivar id: The unique identifier for the verification method.
    :type id: str
    :ivar did_controller: DID who controls the verification method.
    :type did_controller: str
    :ivar issecp256k1: Indicates whether the verification method supports the SECP256k1 curve.
    :type issecp256k1: bool
    :ivar notafter: A datetime value indicating when this verification method expires.
    :type notafter: datetime
    :ivar relationships: A list of verification relationships entities associated with this verification method.
    :type relationships: list[VerificationRelationship]
    :ivar controller: The controller entity of the verification method
    :type controller: Identifier
    """
    __tablename__ = "verification_methods"
    __table_args__ = {'schema': 'public'}

    id: str = Field(primary_key=True)
    did_controller: str = Field(foreign_key="public.identifiers.did",
                                schema_extra={'serialization_alias': 'controller'})
    issecp256k1: bool
    notafter: datetime

    relationships: list["VerificationRelationship"] = Relationship(back_populates="verification_method")
    controller: "Identifier" = Relationship(back_populates="verification_methods")


class VerificationRelationship(VerificationRelationshipBase, table=True):
    """
    Represents a verification relationship table model.

    :ivar id: The unique identifier of the verification relationship.
    :type id: int
    :ivar identifier_did: The DID of the associated identifier.
    :type identifier_did: str
    :ivar vmethodid: The ID of the associated verification method.
    :type vmethodid: str
    :ivar verification_method: The associated verification method entity, establishing a
        bidirectional relationship with the verification method.
    :type verification_method: VerificationMethod
    :ivar identifier: The associated identifier entity
    :type identifier: Identifier
    """
    __tablename__ = "verification_relationships"
    __table_args__ = {'schema': 'public'}

    id: int = Field(primary_key=True, default=None)
    identifier_did: str = Field(foreign_key="public.identifiers.did", schema_extra={'serialization_alias': 'did'})
    vmethodid: str = Field(foreign_key="public.verification_methods.id",
                           schema_extra={'serialization_alias': 'vMethodId'})

    verification_method: VerificationMethod = Relationship(back_populates="relationships")
    identifier: "Identifier" = Relationship(back_populates="verification_relationships")


class IdentifierController(SQLModel, table=True):
    """
    Represents a identifier controller table model.

    :ivar identifier_did: DID of the identifier being
        controlled. Acts as a primary key and references the "did" column in the
        "public.identifiers" table.
    :type identifier_did: str
    :ivar did_controller: DID of the controller that
        has control over the identifier. Acts as a primary key and references the
        "did" column in the "public.identifiers" table.
    :type did_controller: str
    """
    __tablename__ = "identifier_controllers"
    __table_args__ = {'schema': 'public'}

    identifier_did: str = Field(primary_key=True, foreign_key="public.identifiers.did")
    did_controller: str = Field(primary_key=True, foreign_key="public.identifiers.did")


class Identifier(IdentifierBase, table=True):
    """
    Represents a Decentralized Identifier table model.

    :ivar did: The unique identifier for this entry.
    :type did: str
    :ivar context: The context associated with this identifier (optional).
    :type context: str | None
    :ivar created_at: The date and time when the identifier was created.
    :type created_at: datetime
    :ivar tir_authorized: Indicates whether TIR authorization is granted.
    :type tir_authorized: bool
    :ivar tnt_authorized: Indicates whether TNT authorization is granted.
    :type tnt_authorized: bool
    :ivar controllers: List of identifiers that control this identifier.
    :type controllers: list[Identifier]
    :ivar controlled_identifiers: List of identifiers controlled by this identifier.
    :type controlled_identifiers: list[Identifier]
    :ivar verification_methods: List of verification methods associated with this identifier.
    :type verification_methods: list[VerificationMethod]
    :ivar verification_relationships: List of verification relationships associated with this identifier.
    :type verification_relationships: list[VerificationRelationship]
    """
    __tablename__ = "identifiers"
    __table_args__ = {'schema': 'public'}

    did: str = Field(primary_key=True)
    context: str | None = None
    created_at: datetime = Field(default=func.now())
    tir_authorized: bool = False
    tnt_authorized: bool = False

    controllers: list["Identifier"] = Relationship(back_populates="controlled_identifiers",
                                                   link_model=IdentifierController, sa_relationship_kwargs=dict(
            primaryjoin='Identifier.did==IdentifierController.identifier_did',
            secondaryjoin='Identifier.did==IdentifierController.did_controller'))
    controlled_identifiers: list["Identifier"] = Relationship(back_populates="controllers",
                                                              link_model=IdentifierController,
                                                              sa_relationship_kwargs=dict(
                                                                  primaryjoin='Identifier.did==IdentifierController.did_controller',
                                                                  secondaryjoin='Identifier.did==IdentifierController.identifier_did'))
    verification_methods: list[VerificationMethod] = Relationship(back_populates="controller")
    verification_relationships: list[VerificationRelationship] = Relationship(back_populates="identifier")
