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
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jwcrypto import jwk
from sqlmodel import SQLModel
from web3.contract.base_contract import BaseContractFunction

from ebsi_sim.core.config import settings
from ebsi_sim.core.exceptions import RequestError, AuthError, EBSIError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authorisation/token")


class User(SQLModel):
    scopes: list[str]
    sub: str


def to_snakecase(text: str) -> str:
    if text.islower() or not text:
        return text
    return text[0].lower() + ''.join('_' + x.lower() if x.isupper() else x for x in text[1:])


def pem_to_jwk(pem_public_key: str) -> dict:
    try:
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
    except Exception:
        raise EBSIError(f"Error getting JWK")
    else:
        return jwk_dict


vp_scheme = APIKeyHeader(name="Authorization", auto_error=False)


def get_current_user(token: Annotated[str, Depends(vp_scheme)]):
    user = None
    try:
        user: dict = jwt.decode(token, settings.AUTH_PUBLIC_KEY, algorithms=["ES256"],
                                options={'verify_exp': True, "verify_aud": False})
    except jwt.ExpiredSignatureError:
        raise AuthError("Token expired")
    except jwt.exceptions.DecodeError:
        raise AuthError("Invalid token")

    if not user:
        raise AuthError("Impossible to authenticate user")

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
        raise RequestError("Invalid method")


def build_unsigned_transaction(eth_contract, register_address: str, method: str, params: dict) -> dict:
    abi_functions: list[BaseContractFunction] = eth_contract.find_functions_by_name(method)

    params_comparison = params.copy()
    if 'from' in params_comparison:
        params_comparison.pop('from')

    if not len(abi_functions):
        raise RequestError("Invalid method name")

    candidate_function: BaseContractFunction | None = next(
        (tmp_fn for tmp_fn in abi_functions if set(tmp_fn.argument_names) == set(params_comparison.keys())), None)

    if not candidate_function:
        raise RequestError("Invalid arguments")

    abi_args = {k: params[k] for k in candidate_function.argument_names if k in params}

    try:
        unsigned_transaction = candidate_function(**abi_args).build_transaction({"from": params['from'],
                                                                                 "to": register_address,
                                                                                 "nonce": 0xb1d3,
                                                                                 "chainId": 1234,
                                                                                 "gas": 0,
                                                                                 "gasPrice": 0})
    except Exception:
        raise EBSIError("Internal error while building transaction")
    return unsigned_transaction


def exec_signed_transaction(current_user: User, eth_contract, register_address, service, unsigned_transaction,
                            signed_transaction):
    decoded_transaction: Transaction = rlp.decode(bytes.fromhex(signed_transaction), Transaction)
    decoded_transaction_data = decoded_transaction['data']
    if decoded_transaction['data'] != bytes.fromhex(unsigned_transaction['data'].replace("0x", "")):
        raise RequestError("Signed transaction mismatch with unsigned transaction")

    signer = Account.recover_transaction(bytes.fromhex(signed_transaction))
    if signer.lower() != unsigned_transaction['from'].lower():
        raise RequestError("Invalid transaction from")

    if decoded_transaction['to'] != bytes.fromhex(register_address.replace("0x", "")):
        raise RequestError("Invalid transaction to")

    data = decoded_transaction['data']

    func_obj, params = eth_contract.decode_function_input(data=data)

    if "did" in params and current_user.sub != params['did']:
        raise RequestError("Invalid transaction")

    try:
        function = getattr(service, to_snakecase(func_obj.fn_name))

        params_snakecase = {to_snakecase(k): v for k, v in params.items()}

        func_result = function(**params_snakecase)
        return '0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331'
    except AttributeError:
        raise RequestError("Invalid transaction")
    except Exception as e:
        raise EBSIError("Internal error while executing transaction")
