from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.params import Security
from starlette.status import HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

from facts_backend.src.core.auth import get_current_user, User
from facts_backend.src.schemas.article import ArticleCreate
from facts_backend.src.schemas.auth import TokenScopeEnum
from facts_backend.src.schemas.document import DocumentPublic
from facts_backend.src.schemas.shared import BuildTransactionResponse, SignedTransactionPayload, \
    SignedTransactionResponse
from facts_backend.src.services.article import ArticleService

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/", summary="Get a list of articles",
            description="Returns a list of articles. The list can be filtered by creator DID supporting pagination through offset and page size parameters.")
def get_articles(did_creator: str | None = None, offset: int = 0, page_size: int = 100,
                 article_service: ArticleService = Depends()) -> list:
    return article_service.get_articles_list(did_creator=did_creator, offset=offset, page_size=page_size)


@router.get("/by-url", summary="Get an article by URL",
            description="Returns an article by its URL. The article is returned as a JSON object.")
def get_article_by_url(url: str, article_service: ArticleService = Depends()):
    return article_service.get_article_by_url(url)


@router.head("/by-url", summary="Check if an article exists by URL",
             description="Returns a 204 No Content if the article exists, otherwise a 404 Not Found.")
def head_article_by_url(url: str, article_service: ArticleService = Depends()):
    article_exists = article_service.head_article_by_url(url)
    if not article_exists:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Article not found")
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get("/{article_id}", summary="Get an article by hash",
            description="Returns an article by its hash. The article is returned as a JSON object.")
def get_article(article_id: str, article_service: ArticleService = Depends()) -> DocumentPublic:
    return article_service.get_article_by_hash(article_id)


@router.get("/{article_id}/sources", summary="Get the sources chain of an article",
            description="Returns the sources chain of an article. The sources are returned as a JSON list.")
def get_article_sources(article_id: str, article_service: ArticleService = Depends()):
    return article_service.get_article_sources_chain(article_id)


@router.post("/", summary="Builds a transaction to create an article.",
             description="Builds the transaction to create an article. The transaction is returned as a JSON object.")
def create_article_transaction(payload: ArticleCreate,
                               current_user: Annotated[
                                   User, Security(get_current_user,
                                                  scopes=[TokenScopeEnum.scope_publisher_create.value])],
                               article_service: ArticleService = Depends()) -> BuildTransactionResponse:
    return article_service.request_create_article(current_user, payload)


@router.post("/{article_id}/signed", summary="Confirm the creation of an article.",
             description="Receives the signed transaction confirming the creation of an article.")
def confirm_article_transaction(article_id: str, signed_transaction: SignedTransactionPayload,
                                current_user: Annotated[
                                    User, Security(get_current_user,
                                                   scopes=[TokenScopeEnum.scope_publisher_create.value])],
                                article_service: ArticleService = Depends()) -> SignedTransactionResponse:
    return article_service.confirm_create_article(current_user, article_id, signed_transaction)
