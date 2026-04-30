import base64
import hashlib
import json
from typing import Any

import rlp
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from eth_account import Account
from eth_account._utils.legacy_transactions import Transaction, serializable_unsigned_transaction_from_dict
from eth_keys import keys
from eth_utils import to_checksum_address
from jwcrypto import jwk
from web3.contract.base_contract import BaseContractFunction

from ebsi_sim.src.core.auth import User
from ebsi_sim.src.core.exceptions import EBSIRequestError, EBSIError

def to_snakecase(text: str) -> str:
    """
    Converts a given string from CamelCase to snake_case format.

    :param text: The input string to be converted from CamelCase to snake_case.
    :type text: str
    :return: The input string converted to snake_case format.
    :rtype: str
    """
    if text.islower() or not text:
        return text
    return text[0].lower() + ''.join('_' + x.lower() if x.isupper() else x for x in text[1:])


def booleanize(value: str) -> Any:
    """
    Converts a given hexadecimal string representation of a boolean value into its
    corresponding boolean type.

    :param value: A string representing a hexadecimal boolean value.
    :return: Either a boolean (`True` or `False`) if the value matches '0x01' or
        '0x00', respectively, or the original `value` if no matches are found.
    """
    if value == "0x01":
        return True
    if value == "0x00":
        return False
    return value


def pem_to_jwk(pem_public_key: str) -> dict:
    """
    Converts a PEM-encoded public key to a JWK (JSON Web Key) format and includes a
    calculated thumbprint-based `kid` (Key ID) according to RFC 7638.

    :param pem_public_key: A PEM-encoded public key string.
    :type pem_public_key: str
    :raises EBSIError: If the JWK conversion or `kid` generation fails.
    :return: A dictionary representation of the JWK with an added `kid` field.
    :rtype: dict
    """
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

        # Create JSON representation
        canonical_json = json.dumps(required_members, sort_keys=True, separators=(',', ':'))

        # Calculate SHA-256 hash
        hash_bytes = hashlib.sha256(canonical_json.encode('utf-8')).digest()

        # Base64url encode
        kid = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').rstrip('=')

        jwk_dict['kid'] = kid
    except Exception:
        raise EBSIError(f"Error getting JWK")
    else:
        return jwk_dict


def build_unsigned_transaction(eth_contract, register_address: str, method: str, params: dict, public_key_check: bool, allowed_public_keys: list[str]) -> dict:
    """
    Builds an unsigned Ethereum transaction for a specified contract method with provided parameters.

    This function identifies the appropriate contract method from the Ethereum contract's ABI
    that matches the provided method name and arguments. It then constructs an unsigned transaction
    using the specified parameters and a predefined transaction configuration.

    :param eth_contract: The Ethereum contract object providing the ABI for method discovery.
    :param register_address: The hexadecimal address in string format of the target Ethereum contract.
    :param method: The name of the contract method to invoke.
    :param params: A dictionary of parameters for the contract method including the required
                   Ethereum transaction fields like `from`.

    :return: A dictionary representing the unsigned transaction that can be signed and sent
             to the Ethereum network.
    :raises RequestError: If the specified method name is invalid or if the supplied parameters
                          do not match any of the method's argument configurations.
    :raises EBSIError: If an internal issue occurs while building the unsigned transaction.
    """
    if public_key_check:
        is_eth_address_valid = len([pk for pk in allowed_public_keys if public_key_matches_address(pk, params['from'])]) > 0
        if not is_eth_address_valid:
            raise EBSIRequestError("Invalid transaction signer")

    abi_functions: list[BaseContractFunction] = eth_contract.find_functions_by_name(method)

    params_comparison = params.copy()
    if 'from' in params_comparison:
        params_comparison.pop('from')

    if not len(abi_functions):
        raise EBSIRequestError("Invalid method name")

    candidate_function: BaseContractFunction | None = next(
        (tmp_fn for tmp_fn in abi_functions if set(tmp_fn.argument_names) == set(params_comparison.keys())), None)

    if not candidate_function:
        raise EBSIRequestError("Invalid arguments")

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

def get_public_key_from_transaction(decoded_transaction: Transaction, unsigned_transaction: dict):
    r, s, v = decoded_transaction['r'], decoded_transaction['s'], decoded_transaction['v']
    v_standard = v - 27 if v in (27, 28) else (v - 35) % 2
    sig = keys.Signature(vrs=(v_standard, r, s))

    unsigned_transaction.pop("from")
    unsigned_transaction_hash = serializable_unsigned_transaction_from_dict(unsigned_transaction).hash()
    eth_public_key = sig.recover_public_key_from_msg_hash(unsigned_transaction_hash).to_hex()
    return eth_public_key


def public_key_matches_address(public_key_hex: str, eth_address: str) -> bool:
    pub_key_hex = public_key_hex.replace("0x", "")

    # Strip the 0x04 uncompressed prefix if present (eth_keys expects 64 raw bytes)
    if pub_key_hex.startswith("04"):
        pub_key_hex = pub_key_hex[2:]

    pub_key_bytes = bytes.fromhex(pub_key_hex)
    pub_key = keys.PublicKey(pub_key_bytes)

    derived_address = pub_key.to_checksum_address()
    expected_address = to_checksum_address(eth_address)

    return derived_address == expected_address

def exec_signed_transaction(current_user: User, eth_contract, register_address, service, unsigned_transaction,
                            signed_transaction, public_key_check: bool, allowed_public_keys: list[str]) -> str:
    """
    Execute a simulated Ethereum transaction and perform necessary validation checks.

    :param current_user: The user making the request.
    :type current_user: User
    :param eth_contract: The Ethereum smart contract instance to decode the transaction input.
    :type eth_contract: Any
    :param register_address: The Ethereum address to which the transaction is directed.
    :type register_address: str
    :param service: The service containing the functionality to be executed based on the transaction.
    :type service: Any
    :param unsigned_transaction: The unsigned version of the transaction, used for verification.
    :type unsigned_transaction: dict
    :param signed_transaction: The serialized signed transaction in hexadecimal format.
    :type signed_transaction: str
    :param allowed_public_keys: List of public keys allowed to sign the transaction.
    :type allowed_public_keys: list[str]
    :return: A mock hexadecimal confirmation string indicating the transaction was successfully executed.
    :rtype: str
    :raises RequestError: If any validation fails for the transaction data, signer, or addresses.
    :raises EBSIError: If an internal error occurs while executing the transaction.
    """
    decoded_transaction: Transaction = rlp.decode(bytes.fromhex(signed_transaction), Transaction)
    decoded_transaction_data = decoded_transaction['data']
    if decoded_transaction['data'] != bytes.fromhex(unsigned_transaction['data'].replace("0x", "")):
        raise EBSIRequestError("Signed transaction mismatch with unsigned transaction")

    signer = Account.recover_transaction(bytes.fromhex(signed_transaction))
    if signer.lower() != unsigned_transaction['from'].lower():
        raise EBSIRequestError("Invalid transaction from")

    if decoded_transaction['to'] != bytes.fromhex(register_address.replace("0x", "")):
        raise EBSIRequestError("Invalid transaction to")

    if public_key_check:
        eth_public_key = '0x04' + get_public_key_from_transaction(decoded_transaction, unsigned_transaction).replace('0x', '')
        if eth_public_key not in allowed_public_keys:
            raise EBSIRequestError("Transaction signer not allowed for this user")

    data = decoded_transaction['data']

    try:
        func_obj, params = eth_contract.decode_function_input(data=data)
    except Exception:
        raise EBSIRequestError("Impossible to decode and find transaction function (check function name and args)")

    if "did" in params and current_user.sub != params['did']:
        raise EBSIRequestError("User subject is not the same as the transaction signer")

    try:
        # Searches for the function in the service
        function = getattr(service, to_snakecase(func_obj.fn_name))
        params_snakecase = {to_snakecase(k): v for k, v in params.items()}

        # Execute the function with the decoded parameters
        function(**params_snakecase)
    except AttributeError:
        raise EBSIRequestError("Function not found in service class")
    except EBSIError:
        raise
    except Exception as e:
        raise EBSIError("Internal error while executing transaction")
    else:
        # Mock return value confirming the transaction was executed
        return '0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331'
