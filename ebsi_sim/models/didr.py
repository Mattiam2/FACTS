from datetime import datetime

from sqlmodel import SQLModel, Field, func, Relationship

from ebsi_sim.schemas.identifier import IdentifierBase
from ebsi_sim.schemas.verification import VerificationMethodBase, VerificationRelationshipBase


class VerificationMethod(VerificationMethodBase, table=True):
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
    __tablename__ = "verification_relationships"
    __table_args__ = {'schema': 'public'}

    id: int = Field(primary_key=True, default=None)
    identifier_did: str = Field(foreign_key="public.identifiers.did", schema_extra={'serialization_alias': 'did'})
    vmethodid: str = Field(foreign_key="public.verification_methods.id",
                           schema_extra={'serialization_alias': 'vMethodId'})

    verification_method: VerificationMethod = Relationship(back_populates="relationships")
    identifier: "Identifier" = Relationship(back_populates="verification_relationships")

class IdentifierController(SQLModel, table=True):
    __tablename__ = "identifier_controllers"
    __table_args__ = {'schema': 'public'}

    identifier_did: str = Field(primary_key=True, foreign_key="public.identifiers.did")
    did_controller: str = Field(primary_key=True, foreign_key="public.identifiers.did")

class Identifier(IdentifierBase, table=True):
    """
    Represents an EBSI Identifier model for storing and managing identifiers.

    :ivar did: Unique identifier.
    :type id: str
    :ivar created_at: Datetime when the identifier was created.
    :type created_at: datetime
    """

    __tablename__ = "identifiers"
    __table_args__ = {'schema': 'public'}

    did: str = Field(primary_key=True)
    context: str | None = Field(default=None)
    created_at: datetime = Field(default=func.now())
    tir_authorized: bool = Field(default=False)
    tnt_authorized: bool = Field(default=False)

    controllers: list["Identifier"] = Relationship(back_populates="controlled_identifiers", link_model=IdentifierController, sa_relationship_kwargs=dict(primaryjoin='Identifier.did==IdentifierController.identifier_did', secondaryjoin='Identifier.did==IdentifierController.did_controller'))
    controlled_identifiers: list["Identifier"] = Relationship(back_populates="controllers", link_model=IdentifierController, sa_relationship_kwargs=dict(primaryjoin='Identifier.did==IdentifierController.did_controller', secondaryjoin='Identifier.did==IdentifierController.identifier_did'))
    verification_methods: list[VerificationMethod] = Relationship(back_populates="controller")
    verification_relationships: list[VerificationRelationship] = Relationship(back_populates="identifier")
