import base64
import hashlib
import json
from typing import Annotated, Any

import jwt
import rlp
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from eth_account import Account
from eth_account._utils.legacy_transactions import Transaction
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jwcrypto import jwk
from sqlmodel import SQLModel
from starlette.status import HTTP_400_BAD_REQUEST
from web3.contract.base_contract import BaseContractFunction

from ebsi_sim.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authorisation/token")


class User(SQLModel):
    scopes: list[str]
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


def get_current_user(token: Annotated[str, Depends(vp_scheme)]):
    user = None
    try:
        user = jwt.decode(token, settings.AUTH_PUBLIC_KEY, algorithms=["ES256"],
                          options={'verify_exp': False, "verify_aud": False})
    except jwt.exceptions.DecodeError as e:
        pass
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scopes = []
    if "scp" in user:
        scopes = user["scp"].split(" ")
    return User(scopes=scopes, sub=user["sub"])


def booleanize(value: str) -> Any:
    if value == "0x01":
        return True
    if value == "0x00":
        return False
    return value


def check_scopes(user: User, method: str, method_scopes: dict[str, list[str]]):
    if method in method_scopes:
        common_scopes = set(user.scopes) & set(method_scopes[method])
        return len(common_scopes) > 0
    else:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid method")


def build_unsigned_transaction(eth_contract, register_address: str, method: str, params: dict) -> dict:
    abi_functions: list[BaseContractFunction] = eth_contract.find_functions_by_name(method)

    params_comparison = params.copy()
    if 'from' in params_comparison:
        params_comparison.pop('from')

    candidate_function: BaseContractFunction = next(
        (tmp_fn for tmp_fn in abi_functions if set(tmp_fn.argument_names) == set(params_comparison.keys())), None)

    if not candidate_function:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid arguments")

    abi_args = {k: params[k] for k in candidate_function.argument_names if k in params}
    unsigned_transaction = candidate_function(**abi_args).build_transaction({"from": params['from'],
                                                                                  "to": register_address,
                                                                                  "nonce": 0xb1d3,
                                                                                  "chainId": 1234,
                                                                                  "gas": 0,
                                                                                  "gasPrice": 0})
    return unsigned_transaction


def exec_signed_transaction(current_user: User, eth_contract, register_address, service, unsigned_transaction, signed_transaction):
    decoded_transaction: Transaction = rlp.decode(bytes.fromhex(signed_transaction), Transaction)
    decoded_transaction_data = decoded_transaction['data']
    if decoded_transaction['data'] != bytes.fromhex(unsigned_transaction['data'].replace("0x", "")):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Signed transaction mismatch with unsigned transaction")

    signer = Account.recover_transaction(bytes.fromhex(signed_transaction))
    if signer.lower() != unsigned_transaction['from'].lower():
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid transaction from")

    if decoded_transaction['to'] != bytes.fromhex(register_address.replace("0x", "")):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid transaction to")

    data = decoded_transaction['data']

    func_obj, params = eth_contract.decode_function_input(data=data)

    if "did" in params and current_user.sub != params['did']:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid transaction")

    try:
        function = getattr(service, func_obj.fn_name)

        func_result = function(**params)
        return '0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331'
    except Exception as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid transaction")