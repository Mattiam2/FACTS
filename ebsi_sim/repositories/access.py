from ebsi_sim.models import Access
from ebsi_sim.repositories.base import BaseRepository


class AccessRepository(BaseRepository[Access]):
    def __init__(self):
        super().__init__(Access)