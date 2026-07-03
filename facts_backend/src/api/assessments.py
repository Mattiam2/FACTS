from typing import Annotated

from fastapi import APIRouter, Depends, Security, HTTPException, Response
from starlette.status import HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

from facts_backend.src import utils
from facts_backend.src.core.auth import get_current_user, User
from facts_backend.src.schemas.assessment import AssessmentCreate
from facts_backend.src.schemas.auth import TokenScopeEnum
from facts_backend.src.schemas.shared import BuildTransactionResponse, SignedTransactionPayload, \
    SignedTransactionResponse
from facts_backend.src.services.assessment import AssessmentService

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.get("/", summary="Get a list of assessments",
            description="Returns a list of assessments. The list can be filtered by creator DID and article hash supporting pagination through offset and page size parameters.")
def get_assessments(did_creator: str | None = None, article_hash: str | None = None, article_url: str | None = None,
                    offset: int = 0, page_size: int = 100, assessment_service: AssessmentService = Depends()) -> list:
    if article_url is not None:
        article_url = utils.normalize_url(article_url)
    return assessment_service.get_assessments_list(did_creator=did_creator, article_hash=article_hash,
                                                   article_url=article_url, offset=offset, page_size=page_size)


@router.head("/", summary="Check if assessments exist",
             description="Returns a 204 No Content if assessments exist, otherwise a 404 Not Found.")
def head_assessments(did_creator: str | None = None, article_hash: str | None = None, article_url: str | None = None,
                     assessment_service: AssessmentService = Depends()):
    if article_url is not None:
        article_url = utils.normalize_url(article_url)
    assessments_exist = assessment_service.head_assessments_list(did_creator=did_creator, article_hash=article_hash,
                                                                 article_url=article_url)
    if not assessments_exist:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Assessments not found")
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get("/{assessment_id}", summary="Get an assessment by hash",
            description="Returns an assessment by its hash. The assessment is returned as a JSON object.")
def get_assessment(assessment_id: str, assessment_service: AssessmentService = Depends()):
    return assessment_service.get_assessment_document(assessment_id)


@router.get("/{assessment_id}/evidences", summary="Get the evidences of an assessment",
            description="Returns the evidences of an assessment. The evidences are returned as a JSON list.")
def get_assessment_evidences(assessment_id: str, assessment_service: AssessmentService = Depends()):
    return assessment_service.get_assessments_evidences(assessment_id)


@router.post("/", summary="Builds a transaction to create an assessment.",
             description="Builds the transaction to create an assessment. The transaction is returned as a JSON object.")
def create_assessment_transaction(payload: AssessmentCreate,
                                  current_user: Annotated[User, Security(get_current_user, scopes=[
                                      TokenScopeEnum.scope_factchecker_create.value])],
                                  assessment_service: AssessmentService = Depends()) -> BuildTransactionResponse:
    return assessment_service.request_create_assessment(current_user, payload)


@router.post("/{assessment_id}/signed", summary="Confirm the creation of an assessment.",
             description="Receives the signed transaction confirming the creation of an assessment.")
def confirm_assessment_transaction(assessment_id: str, signed_transaction: SignedTransactionPayload,
                                   current_user: Annotated[User, Security(get_current_user, scopes=[
                                       TokenScopeEnum.scope_factchecker_create.value])],
                                   assessment_service: AssessmentService = Depends()) -> SignedTransactionResponse:
    return assessment_service.confirm_create_assessment(current_user, assessment_id, signed_transaction)
