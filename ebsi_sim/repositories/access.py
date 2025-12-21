from ebsi_sim.models import Access
from ebsi_sim.repositories.base import BaseRepository


class AccessRepository(BaseRepository[Access]):
    """
    Handles the access repositories functionality.

    This class inherits from BaseRepository and is specifically
    designed to work with the `Access` type. It provides methods
    and attributes related to managing the access data in the
    underlying repository.
    """

    def __init__(self):
        super().__init__(Access)