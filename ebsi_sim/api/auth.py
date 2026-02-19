import json
import math
from datetime import datetime

from web3 import Web3
from fastapi import APIRouter, HTTPException
from typing import Annotated

from fastapi import Query
from starlette.status import HTTP_400_BAD_REQUEST
from web3.contract.base_contract import BaseContractFunction

from ebsi_sim.core.db import db
from ebsi_sim.repositories.identifier import IdentifierRepository, VerificationRelationshipRepository, \
    VerificationMethodRepository, IdentifierControllerRepository
from ebsi_sim.schemas.identifier import IdentifierListPublic, IdentifierPublic, IdentifierItemPublic
from ebsi_sim.schemas.jsonrpc import JsonRpcCreate, JsonRpcPublic
from ebsi_sim.schemas.presentation import ScopeEnum
from ebsi_sim.schemas.shared import PageLinksPublic
from ebsi_sim.schemas.token import TokenCreate, TokenBase

from ebsi_sim.services import didr

router = APIRouter(prefix="/authorisation", tags=["authorisation"])


@router.post("/token")
def create_token(request: TokenCreate) -> TokenBase:
    pass


@router.get("/.well-known/openid-configuration")
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


@router.get("/jwks")
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


@router.get("/presentation-definitions")
def read_presentation_definitions(scope: ScopeEnum) -> dict:
    path = None
    match scope:
        case scope.tir_write:
            path = f"ebsi_sim/files/tir_write_presentation.json"
        case scope.tnt_write:
            path = f"ebsi_sim/files/tnt_write_presentation.json"
        case scope.tpr_write:
            path = f"ebsi_sim/files/tpr_write_presentation.json"
        case scope.didr_invite:
            path = f"ebsi_sim/files/didr_invite_presentation.json"
        case scope.didr_write:
            path = f"ebsi_sim/files/didr_write_presentation.json"
        case scope.timestamp_write:
            path = f"ebsi_sim/files/timestamp_write_presentation.json"
        case scope.tir_invite:
            path = f"ebsi_sim/files/tir_invite_presentation.json"
        case scope.tnt_authorise:
            path = f"ebsi_sim/files/tnt_authorise_presentation.json"
        case scope.tnt_create:
            path = f"ebsi_sim/files/tnt_create_presentation.json"
        case scope.tsr_write:
            path = f"ebsi_sim/files/tsr_write_presentation.json"
        case _:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid scope")

    return json.load(open(path, "r"))