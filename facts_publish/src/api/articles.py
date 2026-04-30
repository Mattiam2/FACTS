from fastapi import APIRouter, Depends

from facts_publish.src.core.auth import get_current_user, User
from facts_publish.src.schemas.article import ArticlePayload
from facts_publish.src.services.article import ArticleService

router = APIRouter(prefix="/articles")


@router.get("d/")
def get_articles() -> str:
    pass


@router.get("/")
def get_article(url: str, article_service: ArticleService = Depends()):
    return article_service.get_article_by_url(url)


@router.post("/")
def create_article_transaction(payload: ArticlePayload, current_user: User = Depends(get_current_user),
                               article_service: ArticleService = Depends()) -> str:
    return "pippo"


def update_article(article_id: str, article: str) -> str:
    pass


def delete_article(article_id: str) -> str:
    pass
