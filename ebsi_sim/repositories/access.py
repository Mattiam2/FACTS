from ebsi_sim.models import Access
from ebsi_sim.repositories.base import BaseRepository


class AccessRepository(BaseRepository[Access]):
    """
    Handles the storage and retrieval operations for Access instances.
    """

    def __init__(self):
        super().__init__(Access)