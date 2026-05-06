from datetime import datetime
from sqlmodel import Field, Relationship, func, SQLModel, JSON


class Article(SQLModel, table=True):
    __tablename__ = "articles"
    __table_args__ = {'schema': 'public'}

    hash: str = Field(default=None, primary_key=True)
    url: str
    creator: str
    tx_hash: str
    data_hash: str
    timestamp: datetime = Field(default=func.now())
    confirmed: bool
    eth_address: str


class ArticleSource(SQLModel, table=True):
    __tablename__ = "article_sources"
    __table_args__ = {'schema': 'public'}

    article_hash: str = Field(foreign_key="public.articles.hash", primary_key=True)
    source_value: str = Field(primary_key=True)
    source_hash: str | None = Field(default=None)


class Assessment(SQLModel, table=True):
    __tablename__ = "assessments"
    __table_args__ = {'schema': 'public'}

    hash: str = Field(default=None, primary_key=True)
    article_hash: str = Field(foreign_key="public.articles.hash")
    article_url: str
    creator: str
    credibility_score: int
    authenticity_score: int
    tx_hash: str
    data_hash: str
    timestamp: datetime = Field(default=func.now())
    confirmed: bool


class AssessmentEvidence(SQLModel, table=True):
    __tablename__ = "assessment_evidences"
    __table_args__ = {'schema': 'public'}

    assessment_hash: str = Field(foreign_key="public.assessments.hash", primary_key=True)
    evidence_value: str = Field(primary_key=True)
    evidence_hash: str | None = Field(default=None)