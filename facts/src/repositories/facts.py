from facts.src.repositories.facts_base import BaseRepository
from facts.src.models import Article, Assessment, ArticleSource, AssessmentEvidence


class ArticleRepository(BaseRepository[Article]):

    def __init__(self):
        super().__init__(Article)

class ArticleSourceRepository(BaseRepository[ArticleSource]):

    def __init__(self):
        super().__init__(ArticleSource)

class AssessmentRepository(BaseRepository[Assessment]):

    def __init__(self):
        super().__init__(Assessment)

class AssessmentEvidenceRepository(BaseRepository[AssessmentEvidence]):

    def __init__(self):
        super().__init__(AssessmentEvidence)