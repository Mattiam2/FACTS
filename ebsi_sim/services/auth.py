import base64
import hashlib
import json
from typing import Annotated

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jwcrypto import jwk
import jwt

from ebsi_sim.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authorisation/token")

class User:
    scp: str
    sub: str


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

vp_scheme = APIKeyHeader(name="Authorization", auto_error=False)

async def get_current_user(token: Annotated[str, Depends(vp_scheme)]):
    user = jwt.decode(token, settings.public_key, algorithms="ES256", options={'verify_exp': False, "verify_aud": False})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user