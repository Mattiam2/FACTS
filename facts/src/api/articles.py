from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Security

from facts.src.core.auth import get_current_user, User
from facts.src.schemas.article import ArticleCreate
from facts.src.schemas.auth import TokenScopeEnum
from facts.src.schemas.shared import BuildTransactionResponse, SignedTransactionPayload, \
    SignedTransactionResponse
from facts.src.services.article import ArticleService

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/")
def get_articles(did_creator: str | None = None, offset: int = 0, page_size: int = 100,
                 article_service: ArticleService = Depends()) -> list:
    return article_service.get_articles_list(did_creator=did_creator, offset=offset, page_size=page_size)


@router.get("/by-url")
def get_article_by_url(url: str, article_service: ArticleService = Depends()):
    return article_service.get_article_by_url(url)


@router.get("/{article_id}")
def get_article(article_id: str, article_service: ArticleService = Depends()):
    return article_service.get_article_by_hash(article_id)


@router.get("/{article_id}/sources")
def get_article_sources(article_id: str, article_service: ArticleService = Depends()):
    return article_service.get_article_sources_chain(article_id)


@router.post("/")
def create_article_transaction(payload: ArticleCreate,
                               current_user: Annotated[
                                   User, Security(get_current_user, scopes=[TokenScopeEnum.scope_publisher_create.value])],
                               article_service: ArticleService = Depends()) -> BuildTransactionResponse:
    return article_service.request_create_article(current_user, payload)


@router.post("/{article_id}/signed")
def confirm_article_transaction(article_id: str, signed_transaction: SignedTransactionPayload,
                                current_user: Annotated[
                                    User, Security(get_current_user, scopes=[TokenScopeEnum.scope_publisher_create.value])],
                                article_service: ArticleService = Depends()) -> SignedTransactionResponse:
    return article_service.confirm_create_article(current_user, article_id, signed_transaction)
