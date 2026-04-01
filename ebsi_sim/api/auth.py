from fastapi import APIRouter, Depends

from ebsi_sim.core.config import settings
from ebsi_sim.schemas import ScopeEnum, TokenCreate, TokenBase
from ebsi_sim.services.auth import AuthService
from ebsi_sim.services.didr import DidrService
from ebsi_sim.utils import pem_to_jwk

router = APIRouter(prefix="/authorisation", tags=["authorisation"])


@router.post("/token", description="Create an access token given a Verifiable Presentation (VP) token.")
def create_token(payload: TokenCreate, auth_service: AuthService = Depends(),
                 didr_service: DidrService = Depends()) -> TokenBase:
    presentation_definition = auth_service.load_presentation(scope=payload.scope)

    vp_payload = auth_service.get_verifiable_presentation(payload)

    subject_did = didr_service.get_did_document(vp_payload.sub)
    auth_service.check_scope_constraints(payload, subject_did)

    access_token, id_token = auth_service.create_token(vp_payload, payload.scope, payload.presentation_submission,
                                                       presentation_definition)
    return TokenBase(access_token=access_token, id_token=id_token, expires_in=7200, token_type="Bearer",
                     scope=payload.scope.value)


@router.get("/.well-known/openid-configuration", description="OpenID Connect Discovery 1.0 endpoint.")
def openid_configuration() -> dict:
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


@router.get("/jwks", description="JSON Web Key Set (JWK Set) endpoint.")
def read_jwks() -> dict:
    return {
        "keys": [
            pem_to_jwk(settings.AUTH_PUBLIC_KEY)
        ]
    }


@router.get("/presentation-definitions", description="Presentation Definition endpoint.")
def read_presentation_definitions(scope: ScopeEnum) -> dict:
    presentation_definition = AuthService.load_presentation(scope=scope)
    return presentation_definition
