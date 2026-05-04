from facts.src.repositories.facts_base import BaseRepository
from facts.src.models import Article, Assessment


class ArticleRepository(BaseRepository[Article]):

    def __init__(self):
        super().__init__(Article)


class AssessmentRepository(BaseRepository[Assessment]):

    def __init__(self):
        super().__init__(Assessment)