from ebsi_sim.models import Document
from ebsi_sim.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """
    Handles the storage and retrieval operations for Document instances.
    """

    def __init__(self):
        super().__init__(Document)