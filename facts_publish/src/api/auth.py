from fastapi import APIRouter, Depends

from facts_publish.src.schemas.auth import TokenCreate, TokenPublic
from facts_publish.src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["authorisation"])

@router.post("/token", summary="Token Endpoint",
             description="Users receive access tokens after they present a valid EBSI Verifiable Credential and prove ownership over their DID.",
             responses={
                 200: {"description": "Success"},
                 400: {"description": "Bad Request"},
                 500: {"description": "Internal Server Error"}
             })
def create_token(payload: TokenCreate, auth_service: AuthService = Depends()) -> TokenPublic:
    return auth_service.request_token(payload.vp_token, payload.scope)
