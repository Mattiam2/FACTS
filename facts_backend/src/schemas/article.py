from datetime import datetime

from sqlmodel import SQLModel


class ArticleInfoPublic(SQLModel):
    url: str
    title: str
    author: str
    description: str
    publication_date: datetime
    language: str
    sources: list[str]

class ArticleMetadataPublic(SQLModel):
    version: str
    type: str = "FACTS_ARTICLE"
    article_info: ArticleInfoPublic
    eth_address: str
    publisher_vc: str

class ArticleCreate(SQLModel):
    from_eth_address: str
    article_info: ArticleInfoPublic

class ArticleSourceNodePublic(SQLModel):
    article_hash: str
    source_value: str
    source_hash: str | None
    avg_credibility_score: float | None
    avg_manipulation_score: float | None
    depth: int

class ArticleSourceChainPublic(SQLModel):
    root_article_hash: str
    max_depth: int
    nodes: list[ArticleSourceNodePublic]