from typing import Any

from sqlmodel import select, func, literal

from ebsi_sim.core.db import db
from ebsi_sim.models.didr import Identifier, VerificationMethod, VerificationRelationship, IdentifierController
from ebsi_sim.repositories.base import BaseRepository


class IdentifierRepository(BaseRepository[Identifier]):
    """
    Handles the storage and retrieval operations for Identifier instances.
    """

    def __init__(self):
        super().__init__(Identifier)

    def count(self, *, controller: str | None = None, **filters: Any) -> int:
        """
        Counts identifiers based on the given filters and an optional controller.

        :param controller: Optional string representing a specific controller to filter identifiers.
        :param filters: A dictionary of field-value pairs for filtering rows in the `Identifier` table. Only
            rows where all provided fields match the corresponding values in `filters` will be included
            in the count.
        :return: The count of identifiers that match the specified filters and controller.
        :rtype: int
        """
        stmt = select(func.count()).select_from(Identifier)

        for field, value in filters.items():
            if value is not None:
                stmt = stmt.where(getattr(Identifier, field) == value)

        if controller is not None:
            stmt = stmt.where(literal(controller).in_(select(IdentifierController.did_controller).where(
                IdentifierController.identifier_did == Identifier.did)))

        return db.session.scalar(stmt)

    def list(self, *, offset: int = 0, limit: int = 100, order_by: str | None = None, controller: str | None = None,
             **filters: Any) -> list[
        Identifier]:
        """
        Fetches a list of `Identifier` objects from the database based on specified
        criteria

        :param offset: The number of records to skip before starting to return results.
            Defaults to 0.
        :type offset: int | None
        :param limit: The maximum number of records to return. Defaults to 100.
        :type limit: int | None
        :param order_by: The field name by which to sort the results. If None, no
            specific ordering is applied.
        :type order_by: str | None
        :param controller: A controller identifier used to filter the results. If
            provided, only records matching the controller will be returned.
        :type controller: str | None
        :param filters: Additional filtering criteria as keyword arguments. Keys
            represent field names, and values represent the corresponding field
            values to filter by.
        :type filters: dict
        :return: A list of `Identifier` objects satisfying the provided conditions.
        """
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
    """
    Handles data storage and retrieval for IdentifierController instances.
    """

    def __init__(self):
        super().__init__(IdentifierController)


class VerificationMethodRepository(BaseRepository[VerificationMethod]):
    """
    Handles storage and retrieval operations for VerificationMethod instances.
    """

    def __init__(self):
        super().__init__(VerificationMethod)


class VerificationRelationshipRepository(BaseRepository[VerificationRelationship]):
    """
    Handles operations related to VerificationRelationship entities.
    """

    def __init__(self):
        super().__init__(VerificationRelationship)
