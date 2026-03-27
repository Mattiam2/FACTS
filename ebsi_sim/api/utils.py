import json
from datetime import datetime, timedelta
from typing import Annotated
from uuid import uuid4

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey, derive_private_key, SECP256K1
from fastapi import APIRouter, Query

from ebsi_sim.core.config import settings
from ebsi_sim.schemas.verifiable_credential import VerifiableCredentialPublic, VerifiableCredentialPayload

router = APIRouter(prefix="/utils", tags=["utils"])


@router.get("/request_vc")
def request_vc(subject_did: str, credential_type: Annotated[list[str], Query()]) -> str:
    # Return it signed by a DID signer trusting the client whatever.
    # This is necessary in order to make the simulator testable
    # Otherwise I would need to build TAO API which is out of the scope
    issued = datetime.now()
    expirationDate = datetime.now() + timedelta(days=10 * 365)
    uuid_str = uuid4().urn

    credential = VerifiableCredentialPublic(
        context=["https://www.w3.org/2018/credentials/v1"],
        id=uuid_str,
        type=credential_type,
        issuanceDate=issued,
        validFrom=issued,
        validUntil=expirationDate,
        expirationDate=expirationDate,
        issued=issued,
        credentialSubject={'id': subject_did},
        credentialSchema={
            'id': 'https://api-pilot.ebsi.eu/trusted-schemas-registry/v2/schemas/0x23039e6356ea6b703ce672e7cfac0b42765b150f63df78e2bd18ae785787f6a2',
            'type': 'FullJsonSchemaValidator2021'}
    )

    credential_payload = VerifiableCredentialPayload(
        iss=settings.ISSUER_DID,
        sub=subject_did,
        iat=int(issued.timestamp()),
        nbf=int(issued.timestamp()),
        exp=int(expirationDate.timestamp()),
        jti=uuid_str,
        vc=credential
    )

    credential_payload_json = credential_payload.model_dump_json()

    issuer_private_key_bytes = bytes.fromhex(settings.ISSUER_PRIVATE_KEY)
    issuer_private_key = derive_private_key(int.from_bytes(issuer_private_key_bytes), SECP256K1())

    signed_credential = jwt.encode(json.loads(credential_payload_json),
                                   issuer_private_key,
                                   algorithm="ES256K",
                                   headers={
                                       "typ": "JWT",
                                       "alg": "ES256K",
                                       "kid": settings.ISSUER_VMETHOD_ID
                                   })

    return signed_credential
