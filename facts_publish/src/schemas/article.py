from datetime import datetime

from sqlmodel import SQLModel

class ArticleInfo(SQLModel):
    url: str
    title: str
    author: str
    description: str
    publication_date: datetime
    language: str

class ArticlePayload(SQLModel):
    version: str
    type: str
    article_info: ArticleInfo
    sources: list
    publisher_vc: str