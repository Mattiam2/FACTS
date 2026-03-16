from typing import Any

from sqlmodel import select, func, literal

from ebsi_sim.core.db import db
from ebsi_sim.models.didr import Identifier, VerificationMethod, VerificationRelationship, IdentifierController
from ebsi_sim.repositories.base import BaseRepository


class IdentifierRepository(BaseRepository[Identifier]):
    """
    Handles the storage and retrieval operations for Access instances.
    """

    def __init__(self):
        super().__init__(Identifier)

    def count(self, *, controller: str | None = None, **filters: Any) -> int:
        stmt = select(func.count()).select_from(Identifier)

        for field, value in filters.items():
            if value is not None:
                stmt = stmt.where(getattr(Identifier, field) == value)

        if controller is not None:
            stmt = stmt.where(literal(controller).in_(select(IdentifierController.did_controller).where(
                IdentifierController.identifier_did == Identifier.did)))

        return db.session.scalar(stmt)

    def list(self, *, offset=0, limit=100, order_by=None, controller: str | None = None, **filters: Any) -> list[
        Identifier]:
        stmt = select(Identifier)

        for field, value in filters.items():
            if value is not None:
                stmt = stmt.where(getattr(self.model, field) == value)

        if order_by:
            stmt = stmt.order_by(getattr(self.model, order_by))

        if controller is not None:
            stmt = stmt.where(literal(controller).in_(select(IdentifierController.did_controller).where(
                IdentifierController.identifier_did == Identifier.did)))

        stmt = stmt.offset(offset).limit(limit)
        return list(db.session.scalars(stmt))


class IdentifierControllerRepository(BaseRepository[IdentifierController]):

    def __init__(self):
        super().__init__(IdentifierController)


class VerificationMethodRepository(BaseRepository[VerificationMethod]):

    def __init__(self):
        super().__init__(VerificationMethod)


class VerificationRelationshipRepository(BaseRepository[VerificationRelationship]):

    def __init__(self):
        super().__init__(VerificationRelationship)
