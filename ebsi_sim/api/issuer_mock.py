import json
from datetime import datetime, timedelta
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import APIRouter, Query

from ebsi_sim.core.config import settings
from ebsi_sim.schemas.verifiable_credential import VerifiableCredentialPublic, VerifiableCredentialPayload

router = APIRouter(prefix="/issuer-mock", tags=["issuer mock"])


@router.get("/request_vc")
def request_vc(subject_did: Annotated[str, Query(description="DID Subject of the request")],
               credential_type: Annotated[list[str], Query()] = None) -> str:
    """
    Handles the issuance of a Verifiable Credential (VC) simulating an Issuer.
    This endpoint generates a credential containing information about the subject,
    its issuance and expiration, with the required cryptographic signing to ensure
    the credential's validity.
    """
    if credential_type is None:
        credential_type = []
    issued = datetime.now()
    expiration_date = datetime.now() + timedelta(days=10 * 365)
    uuid_str = uuid4().urn

    credential = VerifiableCredentialPublic(
        context=["https://www.w3.org/2018/credentials/v1"],
        id=uuid_str,
        type=credential_type,
        issuanceDate=issued,
        validFrom=issued,
        validUntil=expiration_date,
        expirationDate=expiration_date,
        issued=issued,
        issuer=settings.ISSUER_DID,
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
        exp=int(expiration_date.timestamp()),
        jti=uuid_str,
        vc=credential
    )

    credential_payload_json = credential_payload.model_dump_json()

    signed_credential = jwt.encode(json.loads(credential_payload_json),
                                   settings.ISSUER_ASSERTION_PRIVATE_KEY,
                                   algorithm="ES256",
                                   headers={
                                       "typ": "JWT",
                                       "alg": "ES256",
                                       "kid": settings.ISSUER_ASSERTION_VMETHOD_ID
                                   })

    return signed_credential
