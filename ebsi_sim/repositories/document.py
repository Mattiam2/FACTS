from ebsi_sim.models import Document
from ebsi_sim.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """
    Handles the storage and retrieval operations for Document entities.

    The class serves as a repository layer for performing operations such
    as storing, querying, and managing `Document` entities. It inherits
    from a generic base repository which provides general repository
    functionalities shared across other entities.
    """

    def __init__(self):
        super().__init__(Document)