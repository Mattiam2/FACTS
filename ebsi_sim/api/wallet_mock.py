import json
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

import jwt
from cryptography.hazmat.primitives.asymmetric.ec import derive_private_key, SECP256K1
from fastapi import APIRouter, HTTPException
from web3 import Web3

from ebsi_sim.core.config import settings
from ebsi_sim.schemas.verifiable_presentation import VerifiablePresentationPayload, VerifiablePresentationPublic

router = APIRouter(prefix="/wallet-mock", tags=["wallet mock"])


@router.get("/create_vp")
def create_vp(vc_token: str, did: str, private_key: str, verification_id: Optional[str] = None) -> str:
    """
    Generate a Verifiable Presentation JWT based on the provided Verifiable Credential token,
    holder's DID, and private key. Optionally, include a verification ID in the JWT headers.

    :param vc_token: The Verifiable Credential token to include in the Verifiable Presentation.
    :type vc_token: str
    :param did: The Decentralized Identifier (DID) of the holder of the Verifiable Presentation.
    :type did: str
    :param private_key: The private key of the holder for signing the JWT.
    :type private_key: str
    :param verification_id: The optional identifier for verification to include in the JWT header.
    :type verification_id: Optional[str]
    :return: A signed JSON Web Token (JWT) string representing the Verifiable Presentation.
    :rtype: str
    """
    uuid_str = uuid4().urn

    vp = VerifiablePresentationPublic(
        context=["https://www.w3.org/2018/credentials/v1"],
        id=uuid_str,
        type=["VerifiablePresentation"],
        holder=did,
        verifiableCredential=[
            vc_token
        ]
    )

    vp_payload = VerifiablePresentationPayload(
        iss=did,
        aud=settings.ISSUER_DID,
        sub=did,
        iat=int(datetime.now().timestamp()),
        nbf=int(datetime.now().timestamp()),
        exp=int((datetime.now() + timedelta(days=10 * 365)).timestamp()),
        nonce=uuid_str,
        jti=uuid_str,
        vp=vp
    )

    client_private_key_bytes = bytes.fromhex(private_key)
    client_private_key = derive_private_key(int.from_bytes(client_private_key_bytes), SECP256K1())

    jwt_headers = {"typ": "JWT", "alg": "ES256K"}
    if verification_id:
        jwt_headers['kid'] = verification_id

    return jwt.encode(
        json.loads(vp_payload.model_dump_json()),
        client_private_key,
        algorithm="ES256K",
        headers=jwt_headers
    )


@router.get("/sign_transaction")
def sign_transaction(transaction: str, private_key: str) -> dict:
    """
    Signs an Ethereum transaction using a provided private key and returns a structured
    dictionary with the signed transaction details.

    :param transaction: A JSON string representing the unsigned Ethereum transaction.
    :param private_key: A hexadecimal string representing the private key used to sign
        the transaction.
    :return: A dictionary containing the protocol, the unsigned transaction, the
        components of the signed transaction (r, s, v), and the raw signed transaction in
        hexadecimal format.

    :raises HTTPException: If the transaction is invalid or signing fails due to an
        exception.
    """
    client_private_key_bytes = bytes.fromhex(private_key)

    transaction_dict = json.loads(transaction)
    if "gasLimit" in transaction_dict:
        transaction_dict.pop("gasLimit")

    try:
        signed_transaction = Web3().eth.account.sign_transaction(transaction_dict, client_private_key_bytes)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f'Invalid transaction: {e}')

    data_out = {
        "protocol": "eth",
        "unsignedTransaction": transaction_dict,
        "r": hex(signed_transaction.r),
        "s": hex(signed_transaction.s),
        "v": signed_transaction.v,
        "signedRawTransaction": signed_transaction.raw_transaction.hex()
    }

    return data_out
