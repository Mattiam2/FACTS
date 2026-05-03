from facts.src.models.tnt import Access, Document, Event
from facts.src.repositories.base import BaseRepository


class ArticleRepository(BaseRepository[Access]):

    def __init__(self):
        super().__init__(Access)