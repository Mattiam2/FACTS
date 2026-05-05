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