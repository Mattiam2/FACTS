from fastapi import APIRouter, Depends

from facts.src.core.auth import get_current_user, User
from facts.src.schemas.article import ArticlePayload
from facts.src.schemas.shared import BuildTransactionResponse, SignedTransactionPayload, \
    SignedTransactionResponse
from facts.src.services.article import ArticleService

router = APIRouter(prefix="/articles")


@router.get("d/")
def get_articles(article_service: ArticleService = Depends()) -> str:
    return article_service.get_article_by_url(url)


@router.get("/")
def get_article(url: str, article_service: ArticleService = Depends()):
    return article_service.get_article_by_url(url)


@router.post("/")
def create_article_transaction(payload: ArticlePayload, current_user: User = Depends(get_current_user),
                               article_service: ArticleService = Depends()) -> BuildTransactionResponse:
    return article_service.build_create_transaction(current_user, payload)


@router.post("/{article_id}/signed")
def confirm_article_transaction(article_id: str, signed_transaction: SignedTransactionPayload, current_user: User = Depends(get_current_user),
                               article_service: ArticleService = Depends()) -> SignedTransactionResponse:
    return article_service.send_signed_transaction(current_user, signed_transaction)