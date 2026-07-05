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
        """
        Adds a source to an article identified by its hash.

        :param article_hash: The unique hash of the article to which the source should
            be added.
        :type article_hash: str
        :param source_value: The value or reference representing the source to add.
        :type source_value: str
        :param source_hash: An optional hash or identifier for the source being added.
            If not provided, this can be None.
        :type source_hash: str | None
        :return: None
        :rtype: None
        :raises ValueError: If an article with the given hash is not found.
        """
        article = self.get(article_hash)
        if not article:
            raise ValueError(f"Article with hash {article_hash} not found")
        article.sources.append(ArticleSource(source_value=source_value, source_hash=source_hash))

    def delete_source(self, article_hash: str, source_value: str) -> None:
        """
        Deletes an article source from the database based on the specified article
        hash and source value. If the source exists, it will be removed from
        database.

        :param article_hash: The hash identifying the article.
        :type article_hash: str
        :param source_value: The specific value of the source to delete.
        :type source_value: str
        :return: None
        """
        source = db.session.get(ArticleSource, (article_hash, source_value))
        if source:
            db.session.delete(source)

    def delete_sources(self, article_hash: str) -> None:
        """
        Deletes all sources associated with the specified article.

        :param article_hash: The unique hash of the article whose sources
            should be deleted.
        :type article_hash: str
        :return: None
        """
        article = self.get(article_hash)
        if not article:
            raise ValueError(f"Article with hash {article_hash} not found")
        for source in article.sources:
            db.session.delete(source)

    def delete(self, *, commit=False, id: str) -> None:
        """
        Delete the article with the specified ID (hash) from the database.

        :param commit: Whether to commit the deletion operation. Defaults to False.
        :param id: The unique identifier of the resource to delete.
        :return: None
        """
        self.delete_sources(id)
        super().delete(id=id)

    def get_source_chain(self, article_hash: str, max_depth: int = 10):
        """
        Retrieve the source chain of an article based on its hash while calculating credibility and manipulation
        scores recursively for all related sources.

        This function uses Common Table Expressions (CTEs) to generate a recursive query that provides
        the chain of sources related to the given article. Each source in the chain includes its credibility
        and manipulation scores, calculated as averages based on related assessments.

        :param article_hash: The hash identifier of the article for which the source chain is to be retrieved.
        :type article_hash: str
        :param max_depth: The maximum depth of the source chain to be retrieved. Defaults to 10.
        :type max_depth: int
        :return: A list of tuples representing the source chain. Each tuple consists of the article hash,
                 source value, source hash, averaged credibility score, averaged manipulation score, and depth.
        :rtype: list
        """
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

        recursive = (
            select(
                source_alias.article_hash,
                source_alias.source_value,
                source_alias.source_hash,
                avg_scores_recursive.c.avg_credibility_score,
                avg_scores_recursive.c.avg_manipulation_score,
                (base.c.depth + 1).label("depth")
            ).join(base, source_alias.article_hash == base.c.source_hash)
            .outerjoin(avg_scores_recursive, source_alias.source_hash == avg_scores_recursive.c.article_hash)
            .where(base.c.depth < max_depth)
        )

        full_cte = base.union_all(recursive)

        nodes_list = db.session.execute(select(full_cte).order_by(full_cte.c.depth)).all()
        return nodes_list


class AssessmentRepository(BaseRepository[Assessment]):

    def __init__(self):
        super().__init__(Assessment)

    def add_evidence(self, assessment_hash: str, evidence_value: str, evidence_hash: str | None):
        """
        Adds a new evidence to an existing assessment identified by its hash.

        :param assessment_hash: Unique hash of the assessment.
        :param evidence_value: Value or description of the evidence to be added.
        :param evidence_hash: Optional unique string identifier for the evidence being
            added. Can be None if the evidence is not an URL.
        :return: None
        :raises ValueError: If the assessment associated with the given hash is not
            found in the records.
        """
        assessment = self.get(assessment_hash)
        if not assessment:
            raise ValueError(f"Assessment with hash {assessment_hash} not found")
        assessment.evidences.append(AssessmentEvidence(evidence_value=evidence_value, evidence_hash=evidence_hash))

    def delete_evidence(self, assessment_hash: str, evidence_value: str) -> None:
        """
        Deletes an vidence associated with a given assessment.

        :param assessment_hash: Identifier for the assessment the evidence belongs to.
        :type assessment_hash: str
        :param evidence_value: Value uniquely identifying the evidence to be deleted.
        :type evidence_value: str
        :return: None
        """
        evidence = db.session.get(AssessmentEvidence, (assessment_hash, evidence_value))
        if evidence:
            db.session.delete(evidence)

    def delete_evidences(self, assessment_hash: str) -> None:
        """
        Deletes all evidences associated with the specified assessment.

        :param assessment_hash: The hash identifying the assessment whose evidences
                                need to be deleted.
        :type assessment_hash: str
        :return: None
        :rtype: None
        :raises ValueError: If the assessment corresponding to the given hash is
                            not found.
        """
        assessment = self.get(assessment_hash)
        if not assessment:
            raise ValueError(f"Assessment with hash {assessment_hash} not found")
        for evidence in assessment.evidences:
            db.session.delete(evidence)

    def delete(self, *, commit=False, id: str) -> None:
        """
        Deletes an assessment and its associated evidences from the database.

        :param commit: If set to True, commits the deletion after execution. Defaults to False.
        :type commit: bool
        :param id: The unique identifier of the entity to be deleted.
        :type id: str
        :return: No return value.
        :rtype: None
        """
        self.delete_evidences(id)
        super().delete(id=id)
