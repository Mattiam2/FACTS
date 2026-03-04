from ebsi_sim.models.didr import Identifier, VerificationMethod, VerificationRelationship, IdentifierController
from ebsi_sim.repositories.base import BaseRepository


class IdentifierRepository(BaseRepository[Identifier]):
    """
    Handles the storage and retrieval operations for Access instances.
    """

    def __init__(self):
        super().__init__(Identifier)


class IdentifierControllerRepository(BaseRepository[IdentifierController]):

    def __init__(self):
        super().__init__(IdentifierController)


class VerificationMethodRepository(BaseRepository[VerificationMethod]):

    def __init__(self):
        super().__init__(VerificationMethod)


class VerificationRelationshipRepository(BaseRepository[VerificationRelationship]):

    def __init__(self):
        super().__init__(VerificationRelationship)