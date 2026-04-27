from fastapi import APIRouter, Depends

from ebsi_sim.src.core.config import settings
from ebsi_sim.src.schemas import ScopeEnum, TokenCreate, TokenPublic
from ebsi_sim.src.services.authorisation import AuthService
from ebsi_sim.src.services.didr import DidrService
from ebsi_sim.src.utils import pem_to_jwk

router = APIRouter(prefix="/authorisation", tags=["authorisation"])


@router.post("/token", summary="Token Endpoint",
             description="Users receive access tokens after they present a valid EBSI Verifiable Credential and prove ownership over their DID.",
             responses={
                 200: {"description": "Success"},
                 400: {"description": "Bad Request"},
                 500: {"description": "Internal Server Error"}
             })
def create_token(payload: TokenCreate, auth_service: AuthService = Depends(),
                 didr_service: DidrService = Depends()) -> TokenPublic:
    """
    Users receive access tokens after they present a valid EBSI Verifiable Credential and prove ownership over their DID.
    """
    presentation_definition = auth_service.load_presentation(scope=payload.scope)

    vp_payload = auth_service.get_verifiable_presentation(payload)

    subject_did = didr_service.get_did_document(vp_payload.sub)
    auth_service.check_scope_constraints(payload, subject_did)

    access_token, id_token = auth_service.create_token(vp_payload, payload.scope, payload.presentation_submission,
                                                       presentation_definition)
    return TokenPublic(access_token=access_token, id_token=id_token, expires_in=7200, token_type="Bearer",
                       scope=payload.scope.value)


@router.get("/.well-known/openid-configuration", summary="OpenID Provider Metadata",
            description="Exposes the configuration of the OpenID Provider.",
            responses={
                200: {"description": "OpenID Provider Metadata"},
                500: {"description": "Internal Server Error"}
            })
def openid_configuration() -> dict:
    """
    Exposes the configuration of the OpenID Provider.
    """
    return {
        "issuer": "https://api-pilot.ebsi.eu/authorisation/v4",
        "authorization_endpoint": "https://api-pilot.ebsi.eu/authorisation/v4/authorize",
        "id_token_signing_alg_values_supported": [
            "ES256"
        ],
        "grant_types_supported": [
            "vp_token"
        ],
        "jwks_uri": "https://api-pilot.ebsi.eu/authorisation/v3/jwks",
        "presentation_definition_endpoint": "https://api-pilot.ebsi.eu/authorisation/v4/presentation_definitions",
        "response_types_supported": [
            "vp_token"
        ],
        "request_parameter_supported": True,
        "request_uri_parameter_supported": False,
        "scopes_supported": [
            "openid",
            "didr_invite",
            "didr_write",
            "tir_invite",
            "tir_write",
            "timestamp_write",
            "tnt_authorise",
            "tnt_create",
            "tnt_write",
            "tpr_write",
            "tsr_write"
        ],
        "token_endpoint": "https://api-pilot.ebsi.eu/authorisation/v4/token",
        "subject_types_supported": [
            "public"
        ],
        "token_endpoint_auth_methods_supported": [
            "private_key_jwt"
        ],
        "request_authentication_methods_supported": {
            "token_endpoint": [
                "vp_token"
            ]
        },
        "vp_formats_supported": {
            "jwt_vp": {
                "alg_values_supported": [
                    "ES256"
                ]
            },
            "jwt_vp_json": {
                "alg_values_supported": [
                    "ES256"
                ]
            },
            "jwt_vc": {
                "alg_values_supported": [
                    "ES256"
                ]
            },
            "jwt_vc_json": {
                "alg_values_supported": [
                    "ES256"
                ]
            }
        },
        "subject_syntax_types_supported": [
            "did:key",
            "did:ebsi"
        ],
        "subject_trust_frameworks_supported": [
            "ebsi"
        ],
        "id_token_types_supported": [
            "subject_signed_id_token"
        ]
    }


@router.get("/jwks", summary="OpenID Provider's public keys",
            description="Exposes the public keys of the Authorisation Service in JSON Web Key Set (JWKS) format.",
            responses={
                200: {"description": "JSON Web Key Set"},
                500: {"description": "Internal Server Error"}
            })
def read_jwks() -> dict:
    """
    Exposes the public keys of the Authorisation Service in JSON Web Key Set (JWKS) format.
    """
    return {
        "keys": [
            pem_to_jwk(settings.AUTH_PUBLIC_KEY)
        ]
    }


@router.get("/presentation-definitions", summary="Presentation definition requirements",
            description="Retrieves the presentation definition requirements associated with various OpenID Connect (OIDC) scopes.",
            responses={
                200: {"description": "Success"},
                400: {"description": "Bad Request"},
                500: {"description": "Internal Server Error"}
            })
def read_presentation_definitions(scope: ScopeEnum) -> dict:
    """
    Retrieves the presentation definition requirements associated with various OpenID Connect (OIDC) scopes.
    """
    presentation_definition = AuthService.load_presentation(scope=scope)
    return presentation_definition
