import base64
import hashlib
import json
import math
import jwt
from ..core.config import settings
from datetime import datetime
from jsonpath_ng import parse
from uuid import uuid4
from jwcrypto import jwk
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.backends import default_backend

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
from ebsi_sim.schemas.token import TokenCreate, TokenBase, PresentationSubmission, PresentationDescriptor
from jsonschema import validate, ValidationError

from ebsi_sim.services import didr

router = APIRouter(prefix="/authorisation", tags=["authorisation"])


def pem_to_jwk(pem_public_key: str) -> dict:
    public_key_obj = load_pem_public_key(pem_public_key.encode(), backend=default_backend())
    jwk_key = jwk.JWK.from_pyca(public_key_obj)
    jwk_dict = json.loads(jwk_key.export_public())

    # Calculate thumbprint for KID
    # RFC 7638: JWK Thumbprint
    required_members = {
        'crv': jwk_dict.get('crv'),
        'kty': jwk_dict.get('kty'),
        'x': jwk_dict.get('x'),
        'y': jwk_dict.get('y')
    }

    # Create canonical JSON representation (sorted keys, no whitespace)
    canonical_json = json.dumps(required_members, sort_keys=True, separators=(',', ':'))

    # Calculate SHA-256 hash
    hash_bytes = hashlib.sha256(canonical_json.encode('utf-8')).digest()

    # Base64url encode (without padding)
    kid = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').rstrip('=')

    jwk_dict['kid'] = kid

    return jwk_dict


@router.post("/token")
def create_token(request: TokenCreate) -> TokenBase:
    match request.scope:
        case request.scope.tir_write:
            path = f"ebsi_sim/files/presentation_tir_write.json"
        case request.scope.tnt_write:
            path = f"ebsi_sim/files/presentation_tnt_write.json"
        case request.scope.tpr_write:
            path = f"ebsi_sim/files/presentation_tpr_write.json"
        case request.scope.didr_invite:
            path = f"ebsi_sim/files/presentation_didr_invite.json"
        case request.scope.didr_write:
            path = f"ebsi_sim/files/presentation_didr_write.json"
        case request.scope.timestamp_write:
            path = f"ebsi_sim/files/presentation_timestamp_write.json"
        case request.scope.tir_invite:
            path = f"ebsi_sim/files/presentation_tir_invite.json"
        case request.scope.tnt_authorise:
            path = f"ebsi_sim/files/presentation_tnt_authorise.json"
        case request.scope.tnt_create:
            path = f"ebsi_sim/files/presentation_tnt_create.json"
        case request.scope.tsr_write:
            path = f"ebsi_sim/files/presentation_tsr_write.json"
        case _:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid scope")
    presentation_definition = json.load(open(path, "r"))

    if request.presentation_submission.definition_id != presentation_definition["id"]:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid presentation definition")

    credentials = []

    for descriptor in request.presentation_submission.descriptor_map:
        credentials.append(find_credential(request.vp_token, descriptor, presentation_definition))

    expires_in = 7200
    iat = math.floor(datetime.utcnow().timestamp())
    exp = iat + expires_in
    pem_pub_key = settings.public_key
    jwk_pub_key = pem_to_jwk(pem_pub_key)
    kid = jwk_pub_key["kid"]

    access_token = jwt.encode({
        "aud": "https://api-pilot.ebsi.eu/authorisation/v4",
        "exp": exp,
        "iat": iat,
        "iss": "https://api-pilot.ebsi.eu/authorisation/v4",
        "jti": str(uuid4()),
        "scp": request.scope.value,
        "sub": credentials[0]["sub"],
    },
        settings.private_key,
        "ES256",
        {
            "alg": "ES256",
            "kid": kid,
            "typ": "JWT"
        }
    )

    id_token = jwt.encode({
        "aud": credentials[0]["iss"],
        "exp": exp,
        "iat": iat,
        "iss": "https://api-pilot.ebsi.eu/authorisation/v4",
        "jti": str(uuid4()),
        "nonce": 0,
        "sub": credentials[0]["sub"],
    },
        settings.private_key,
        "ES256",
        {
            "alg": "ES256",
            "kid": kid,
            "typ": "JWT"
        }
    )
    return TokenBase(access_token=access_token, id_token=id_token, expires_in=expires_in, token_type="Bearer", scope=request.scope.value)


def find_credential(token_payload, submission: PresentationDescriptor, presentation_definition):
    credential_id = submission.id
    credential_path = submission.path
    credential_format = submission.format

    descriptor_algos = presentation_definition["format"]
    descriptor_constraints = []

    for in_desc in presentation_definition["input_descriptors"]:
        if in_desc["id"] == credential_id:
            descriptor_algos.update(in_desc["format"])
            descriptor_constraints.extend(in_desc["constraints"]["fields"])
            break

    credential_algo = descriptor_algos[credential_format]["alg"]

    jsonpath_expr = parse(credential_path)
    match_payload = jsonpath_expr.find(token_payload)[0]

    decoded_payload = jwt.decode(match_payload.value, settings.public_key, algorithms=credential_algo,
                                 options={'verify_exp': False, "verify_aud": False, })

    if not submission.path_nested:
        for constraint in descriptor_constraints:
            for const_path in constraint["path"]:
                jsonpath_expr = parse(const_path)
                match_field = jsonpath_expr.find(decoded_payload)[0]
                validate(match_field.value, constraint["filter"])
        return decoded_payload
    else:
        return find_credential(decoded_payload, submission.path_nested, presentation_definition)


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
            path = f"ebsi_sim/files/presentation_tir_write.json"
        case scope.tnt_write:
            path = f"ebsi_sim/files/presentation_tnt_write.json"
        case scope.tpr_write:
            path = f"ebsi_sim/files/presentation_tpr_write.json"
        case scope.didr_invite:
            path = f"ebsi_sim/files/presentation_didr_invite.json"
        case scope.didr_write:
            path = f"ebsi_sim/files/presentation_didr_write.json"
        case scope.timestamp_write:
            path = f"ebsi_sim/files/presentation_timestamp_write.json"
        case scope.tir_invite:
            path = f"ebsi_sim/files/presentation_tir_invite.json"
        case scope.tnt_authorise:
            path = f"ebsi_sim/files/presentation_tnt_authorise.json"
        case scope.tnt_create:
            path = f"ebsi_sim/files/presentation_tnt_create.json"
        case scope.tsr_write:
            path = f"ebsi_sim/files/presentation_tsr_write.json"
        case _:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid scope")

    return json.load(open(path, "r"))
