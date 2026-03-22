import json

from fastapi import APIRouter, HTTPException, Depends
from starlette.status import HTTP_400_BAD_REQUEST

from ebsi_sim.schemas import ScopeEnum, TokenCreate, TokenBase
from ebsi_sim.services.auth import AuthService
from ebsi_sim.services.didr import DidrService

router = APIRouter(prefix="/authorisation", tags=["authorisation"])


@router.post("/token", description="Create an access token given a Verifiable Presentation (VP) token.")
def create_token(request: TokenCreate, auth_service: AuthService = Depends(),
                 didr_service: DidrService = Depends()) -> TokenBase:
    presentation_definition = AuthService.load_presentation(scope=request.scope)

    if request.presentation_submission.definition_id != presentation_definition["id"]:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid presentation definition")

    vp_decoded = auth_service.decode_and_check_signature(request.vp_token, "authentication")

    subject_did = didr_service.getDidDocument(vp_decoded["sub"])

    if request.scope == ScopeEnum.tnt_create and not subject_did.tnt_authorized:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="DID not authorized to this scope")

    holder_did = didr_service.getDidDocument(vp_decoded["vp"]["holder"])

    credentials = auth_service.extract_and_validate_credentials(vp_decoded, request.presentation_submission,
                                                                presentation_definition)

    if request.scope == ScopeEnum.didr_invite and holder_did:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="DID is already registered")
    elif not holder_did:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="DID is not registered")

    access_token = AuthService.create_access_token(request.scope, credentials[0]["sub"])

    id_token = AuthService.create_id_token(subject=credentials[0]["sub"], issuer=credentials[0]["iss"])

    return TokenBase(access_token=access_token, id_token=id_token, expires_in=7200, token_type="Bearer",
                     scope=request.scope.value)


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
            {
                "kty": "EC",
                "crv": "P-256",
                "alg": "ES256",
                "x": "9Cn5hmFfG-uVuixEk4zCdeF6ZLeeWuvqfGPPWMKDKOw",
                "y": "yNnt9p06g8gzoKToQZwzJ-7z6ES-dR2PkyV6oQecaUA",
                "kid": "hcpxQ2xL8ncXKB9SoEgW2ImiG_4WR5NXJvQ_PGuHO5k"
            }
        ]
    }


@router.get("/presentation-definitions", description="Presentation Definition endpoint.")
def read_presentation_definitions(scope: ScopeEnum) -> dict:
    path = None
    match scope:
        case scope.tir_write:
            path = f"ebsi_sim/includes/presentation_tir_write.json"
        case scope.tnt_write:
            path = f"ebsi_sim/includes/presentation_tnt_write.json"
        case scope.tpr_write:
            path = f"ebsi_sim/includes/presentation_tpr_write.json"
        case scope.didr_invite:
            path = f"ebsi_sim/includes/presentation_didr_invite.json"
        case scope.didr_write:
            path = f"ebsi_sim/includes/presentation_didr_write.json"
        case scope.timestamp_write:
            path = f"ebsi_sim/includes/presentation_timestamp_write.json"
        case scope.tir_invite:
            path = f"ebsi_sim/includes/presentation_tir_invite.json"
        case scope.tnt_authorise:
            path = f"ebsi_sim/includes/presentation_tnt_authorise.json"
        case scope.tnt_create:
            path = f"ebsi_sim/includes/presentation_tnt_create.json"
        case scope.tsr_write:
            path = f"ebsi_sim/includes/presentation_tsr_write.json"
        case _:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid scope")

    return json.load(open(path, "r"))
