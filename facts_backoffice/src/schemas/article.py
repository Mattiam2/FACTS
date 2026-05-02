from datetime import datetime

from sqlmodel import SQLModel

class ArticleInfo(SQLModel):
    url: str
    title: str
    author: str
    description: str
    publication_date: datetime
    language: str

class ArticleMetadataCreate(SQLModel):
    version: str
    type: str
    article_info: ArticleInfo
    sources: list

class ArticleMetadataPublic(SQLModel):
    version: str
    type: str
    article_info: ArticleInfo
    sources: list
    publisher_vc: str

class ArticlePayload(SQLModel):
    from_eth_address: str
    article_metadata: ArticleMetadataCreate