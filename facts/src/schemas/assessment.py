from datetime import datetime
from enum import IntEnum

from sqlmodel import SQLModel


class AssessedArticleInfo(SQLModel):
    title: str
    author: str
    description: str
    publication_date: datetime
    language: str
    sources: list[str]


class CredibilityScore(IntEnum):
    FALSE = 1
    PARTIALLY_FALSE = 2
    MISSING_CONTEXT = 3
    SUBJECTIVE = 4
    TRUE = 5


class AuthenticityScore(IntEnum):
    TOTALLY_MANIPULATED = 1  # Exactly 100% of content is artificially produced
    HEAVILY_MANIPULATED = 2  # More than 75% of content is artificially produced
    PARTIALLY_MANIPULATED = 3  # 25% to 75% of content is artificially produced
    MINOR_EDITS = 4  # Less than 25% of content is artificially produced
    AUTHENTIC = 5  # Exactly 0% of content is artificially produced


class BaseEvaluation(SQLModel):
    note: str


class AssessmentCredibilityEvaluation(BaseEvaluation):
    score: CredibilityScore


class AssessmentAuthenticityEvaluation(BaseEvaluation):
    score: AuthenticityScore


class AssessmentInfo(SQLModel):
    article_url: str
    assessment_date: datetime
    credibility_evaluation: AssessmentCredibilityEvaluation
    authenticity_evaluation: AssessmentAuthenticityEvaluation
    evidences: list[str]


class AssessmentMetadata(SQLModel):
    version: str
    type: str = "FACTS_ASSESSMENT"
    assessed_article: AssessedArticleInfo | None
    assessment_info: AssessmentInfo
    eth_address: str
    fact_checker_vc: str


class AssessmentPayload(SQLModel):
    from_eth_address: str
    assessed_article: AssessedArticleInfo | None
    assessment_info: AssessmentInfo
