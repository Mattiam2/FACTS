from app.models import Access
from app.repositories.base import BaseRepository


class AccessRepository(BaseRepository[Access]):
    def __init__(self):
        super().__init__(Access)