from sqlalchemy import literal, func
from sqlalchemy.orm import aliased
from sqlmodel import select

from facts_backend.src.core.db import db
from facts_backend.src.models import Article, Assessment, ArticleSource, AssessmentEvidence
from facts_backend.src.repositories.facts_base import BaseRepository


class ArticleRepository(BaseRepository[Article]):

    def __init__(self):
        super().__init__(Article)

    def add_source(self, article_hash: str, source_value: str, source_hash: str | None):
        article = self.get(article_hash)
        if not article:
            raise ValueError(f"Article with hash {article_hash} not found")
        article.sources.append(ArticleSource(source_value=source_value, source_hash=source_hash))

    def delete_source(self, article_hash: str, source_value: str) -> None:
        source = db.session.get(ArticleSource, (article_hash, source_value))
        if source:
            db.session.delete(source)

    def delete_sources(self, article_hash: str) -> None:
        article = self.get(article_hash)
        if not article:
            raise ValueError(f"Article with hash {article_hash} not found")
        for source in article.sources:
            db.session.delete(source)

    def delete(self, *, commit=False, id: str) -> None:
        self.delete_sources(id)
        super().delete(id=id)

    def get_source_chain(self, article_hash: str):

        avg_scores = (
            select(
                Assessment.article_hash,
                func.avg(Assessment.credibility_score).label("avg_credibility_score"),
                func.avg(Assessment.manipulation_score).label("avg_manipulation_score"),
            )
            .group_by(Assessment.article_hash)
            .subquery("average_articles")
        )

        # Base CTE
        base = (
            select(
                ArticleSource.article_hash,
                ArticleSource.source_value,
                ArticleSource.source_hash,
                avg_scores.c.avg_credibility_score,
                avg_scores.c.avg_manipulation_score,
                literal(0).label("depth")
            )
            .outerjoin(avg_scores, ArticleSource.source_hash == avg_scores.c.article_hash)
            .where(ArticleSource.article_hash == article_hash).cte(name="source_chain", recursive=True))

        # Recursive
        source_alias = aliased(ArticleSource)

        avg_scores_recursive = (
            select(
                Assessment.article_hash,
                func.avg(Assessment.credibility_score).label("avg_credibility_score"),
                func.avg(Assessment.manipulation_score).label("avg_manipulation_score")
            )
            .group_by(Assessment.article_hash)
            .subquery("average_articles_r")
        )

        recursive = (select(
            source_alias.article_hash,
            source_alias.source_value,
            source_alias.source_hash,
            avg_scores_recursive.c.avg_credibility_score,
            avg_scores_recursive.c.avg_manipulation_score,
            (base.c.depth + 1).label("depth")
        ).join(base, source_alias.article_hash == base.c.source_hash)
                     .outerjoin(avg_scores_recursive, source_alias.source_hash == avg_scores_recursive.c.article_hash)
                     )

        full_cte = base.union_all(recursive)

        nodes_list = db.session.execute(select(full_cte).order_by(full_cte.c.depth)).all()
        return nodes_list


class AssessmentRepository(BaseRepository[Assessment]):

    def __init__(self):
        super().__init__(Assessment)

    def add_evidence(self, assessment_hash: str, evidence_value: str, evidence_hash: str | None):
        assessment = self.get(assessment_hash)
        if not assessment:
            raise ValueError(f"Assessment with hash {assessment_hash} not found")
        assessment.evidences.append(AssessmentEvidence(evidence_value=evidence_value, evidence_hash=evidence_hash))

    def delete_evidence(self, assessment_hash: str, evidence_value: str) -> None:
        evidence = db.session.get(AssessmentEvidence, (assessment_hash, evidence_value))
        if evidence:
            db.session.delete(evidence)

    def delete_evidences(self, assessment_hash: str) -> None:
        assessment = self.get(assessment_hash)
        if not assessment:
            raise ValueError(f"Assessment with hash {assessment_hash} not found")
        for evidence in assessment.evidences:
            db.session.delete(evidence)

    def delete(self, *, commit=False, id: str) -> None:
        self.delete_evidences(id)
        super().delete(id=id)
