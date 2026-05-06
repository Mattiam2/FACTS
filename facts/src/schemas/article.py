from datetime import datetime

from sqlmodel import SQLModel

class ArticleInfo(SQLModel):
    url: str
    title: str
    author: str
    description: str
    publication_date: datetime
    language: str
    sources: list[str]

class ArticleMetadata(SQLModel):
    version: str
    type: str = "FACTS_ARTICLE"
    article_info: ArticleInfo
    eth_address: str
    publisher_vc: str

class ArticlePayload(SQLModel):
    from_eth_address: str
    article_info: ArticleInfo

class ArticleSourceChainNode(SQLModel):
    article_hash: str
    source_value: str
    source_hash: str | None
    depth: int

class ArticleSourceChainResponse(SQLModel):
    root_article_hash: str
    max_depth: int
    nodes: list[ArticleSourceChainNode]