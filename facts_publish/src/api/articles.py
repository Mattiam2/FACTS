from fastapi import APIRouter, Depends

from facts_publish.src.services.article import ArticleService

router = APIRouter(prefix="/articles")

@router.get("d/")
def get_articles() -> str:
    pass

@router.get("/")
def get_article(url: str, article_service: ArticleService = Depends()):
    return article_service.get_article_by_url(url)


def create_article(article: str) -> str:
    pass

def update_article(article_id: str, article: str) -> str:
    pass

def delete_article(article_id: str) -> str:
    pass