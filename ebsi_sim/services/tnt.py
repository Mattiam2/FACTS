import hashlib
import json
import time
from datetime import datetime

from fastapi import Depends
from web3 import Web3
from web3.contract import Contract

from ebsi_sim.core.config import settings
from ebsi_sim.core.exceptions import RequestError, NotFoundError, AuthError, EBSIError
from ebsi_sim.repositories.didr import IdentifierRepository
from ebsi_sim.repositories.tnt import AccessRepository
from ebsi_sim.repositories.tnt import DocumentRepository
from ebsi_sim.repositories.tnt import EventRepository
from ebsi_sim.schemas import JsonRpcCreate, PermissionEnum
from ebsi_sim.schemas.event import EventParams
from ebsi_sim.utils import check_scopes, User, build_unsigned_transaction, exec_signed_transaction, booleanize


class TntServiceError(EBSIError):
    """
    Represents an error specific to TNT service operations (Status Code: 500).
    """
    pass


class TntServiceAuthError(TntServiceError, AuthError):
    """
    Represents an TNT service authentication error (Status Code: 401).
    """
    pass


class TntServiceNotFoundError(TntServiceError, NotFoundError):
    """
    Represents an error raised when a specific resource is not found (Status Code: 404).
    """
    pass


class TntServiceRequestError(TntServiceError, RequestError):
    """
    Represents an error that occurs during an TNT service request.
    """
    pass


class TntService:
    eth_contract: type[Contract]
    document_repository: DocumentRepository
    access_repository: AccessRepository
    event_repository: EventRepository
    identifier_repository: IdentifierRepository
    tnt_abi: dict

    def __init__(self, document_repository: DocumentRepository = Depends(),
                 access_repository: AccessRepository = Depends(), event_repository: EventRepository = Depends(),
                 identifier_repository: IdentifierRepository = Depends()):
        self.document_repository = document_repository
        self.access_repository = access_repository
        self.event_repository = event_repository
        self.identifier_repository = identifier_repository

        self.tnt_abi = json.load(open("ebsi_sim/includes/abi_tnt.json", "r"))
        self.eth_contract = Web3().eth.contract(abi=self.tnt_abi)

    def get_document(self, document_hash: bytes | str):
        if isinstance(document_hash, bytes):
            document_hash = "0x" + document_hash.hex()
        return self.document_repository.get(document_hash)

    def count_documents(self, **filters):
        return self.document_repository.count(**filters)

    def list_documents(self, *, offset: int = 0, limit: int = 100, order_by: str | None = None, **filters):
        return self.document_repository.list(offset=offset, limit=limit, order_by=order_by, **filters)

    def count_accesses(self, **filters):
        return self.access_repository.count(**filters)

    def list_accesses(self, *, offset: int = 0, limit: int = 100, order_by: str | None = None, **filters):
        return self.access_repository.list(offset=offset, limit=limit, order_by=order_by, **filters)

    def count_events(self, **filters):
        return self.event_repository.count(**filters)

    def list_events(self, *, offset: int = 0, limit: int = 100, order_by: str | None = None, **filters):
        return self.event_repository.list(offset=offset, limit=limit, order_by=order_by, **filters)

    def authorise_did(self, *, sender_did: str, authorised_did: str, white_list: bool):
        """
        JSON RPC Method: Authorises a decentralized identifier (DID) to operate on TNT documents

        :param sender_did: The DID of the sender performing the authorization
                          operation.
        :param authorised_did: The DID of the entity being authorised or
                               de-authorised.
        :param white_list: A flag indicating whether the `authorised_did` is to be
                           added (`True`) or removed (`False`) from the authorised
                           list.
        :return: None
        """
        self.identifier_repository.update(id=authorised_did, tnt_authorized=white_list)

    def create_document(self, *, document_hash: bytes | str, document_metadata: str, did_ebsi_creator: str,
                        timestamp: int | None = None, timestamp_proof: bytes | str | None = None):
        """
        JSON RPC Method: Creates a document in the database with the provided metadata, hash, and optional timestamp information.

        :param document_hash: Hash of the document to be created. The hash can be provided as a string or bytes.
        :param document_metadata: Metadata of the document represented as a string in hexadecimal format. The metadata
            should be decoded before being stored.
        :param did_ebsi_creator: DID of the creator in EBSI format as a string.
        :param timestamp: (Optional) Integer Unix timestamp representing the creation time of the document.
        :param timestamp_proof: (Optional) Proof of the timestamp, provided as a string or bytes. If provided, the
            source will be marked as "external"; otherwise, it defaults to "block".
        :return: None
        """
        doc_metadata = bytes.fromhex(document_metadata[2:]).decode('utf-8')
        doc_timestamp_datetime = datetime.fromtimestamp(timestamp) if timestamp else None
        doc_timestamp_proof = timestamp_proof

        if isinstance(document_hash, bytes):
            document_hash = "0x" + document_hash.hex()

        if doc_timestamp_proof and isinstance(doc_timestamp_proof, bytes):
            doc_timestamp_proof = "0x" + doc_timestamp_proof.hex()

        self.document_repository.create(id=document_hash, creator=did_ebsi_creator,
                                        metadata_text=doc_metadata,
                                        timestamp_datetime=doc_timestamp_datetime, timestamp_proof=doc_timestamp_proof,
                                        timestamp_source="external" if doc_timestamp_proof else "block")

    def remove_document(self, *, document_hash: bytes | str):
        """
        JSON RPC Method: Removes a document with the given document hash from the repository.

        :param document_hash: The hash of the document to be removed. This can be
                              provided as a string or bytes.
        :type document_hash: bytes | str

        :return: None
        """
        if isinstance(document_hash, bytes):
            document_hash = "0x" + document_hash.hex()
        self.document_repository.delete(id=document_hash)

    def grant_access(self, *, document_hash: bytes | str, granted_by_account: bytes | str, subject_account: bytes | str,
                     permission: str):
        """
        JSON RPC Method: Grants access to a specific document by assigning permissions to a subject account. The
        permission type ('write' or 'delegate') is determined based on the provided integer value.

        :param document_hash: The unique identifier for the document, represented as a bytes
            object or a hexadecimal string.
        :param granted_by_account: The account address that grants the access, represented as
            a bytes object or a hexadecimal string.
        :param subject_account: The account address that will receive the permissions, represented
            as a bytes object or a hexadecimal string.
        :param permission: A string representing the permission type for access. If the provided
            value can be interpreted as an integer, it will be converted into 'write' (non-zero)
            or 'delegate' (zero).
        :return: None
        """
        if isinstance(document_hash, bytes):
            document_hash = "0x" + document_hash.hex()
        if isinstance(granted_by_account, bytes):
            granted_by_account = "0x" + granted_by_account.hex()
        if isinstance(subject_account, bytes):
            subject_account = "0x" + subject_account.hex()
        # granted_by_type = access['grantedByAccType']
        # subject_type = access['subjectAccType']
        permission = "write" if int(permission, 0) else "delegate"
        self.access_repository.create(subject=subject_account, document_id=document_hash, granted_by=granted_by_account,
                                      permission=permission)

    def revoke_access(self, *, document_hash: bytes | str, revoked_by_account: bytes | str,
                      subject_account: bytes | str, permission: str):
        """
        JSON RPC Method: Revokes a specific permission for a subject account on a document.

        :param document_hash: The unique identifier (hash) of the document. This can be
            provided as either a byte string or a hexadecimal string format.
        :param revoked_by_account: The account identifier of the entity initiating the
            revocation, provided as either a byte string or a hexadecimal string format.
        :param subject_account: The account identifier of the subject whose access is
            being revoked, provided as either a byte string or a hexadecimal string format.
        :param permission: The type of access permission being revoked. It determines
            if the access is 'write' (if the permission evaluates to a truthy integer)
            or 'delegate' (if the permission evaluates to a falsy integer).
        :return: None
        """
        if isinstance(document_hash, bytes):
            document_hash = "0x" + document_hash.hex()
        if isinstance(revoked_by_account, bytes):
            revoked_by_account = "0x" + revoked_by_account.hex()
        if isinstance(subject_account, bytes):
            subject_account = "0x" + subject_account.hex()
        permission = "write" if int(permission, 0) else "delegate"
        revoked_access = \
        self.access_repository.list(subject=subject_account, document_id=document_hash, permission=permission)[
            0]
        self.access_repository.delete(id=revoked_access.id)

    def write_event(self, *, event_params: EventParams, timestamp: int | None = None,
                    timestamp_proof: bytes | str | None = None):
        """
        JSON RPC Method: Writes an event to the database using the provided event parameters,
        timestamp, and timestamp proof.

        :param event_params: A dictionary containing the parameters of the event,
            including `documentHash` (bytes or str), `externalHash` (str),
            `sender` (bytes or str), `origin` (str), and `metadata` (str).
        :param timestamp: An optional timestamp for the event as a UNIX timestamp.
            If not provided, the timestamp will be set to None.
        :param timestamp_proof: Optional proof for the timestamp. This can be in bytes
            or as a hexadecimal string. If bytes are provided, it will be converted to
            a hexadecimal string before use.
        :return: None
        """
        doc_id = "0x" + event_params['documentHash'].hex() if isinstance(event_params['documentHash'], bytes) else \
        event_params['documentHash']
        external_hash = event_params['externalHash']
        sender = event_params['sender'].decode('utf-8') if isinstance(event_params['sender'], bytes) else event_params[
            'sender']
        origin = event_params['origin']
        metadata = event_params['metadata']
        event_timestamp_datetime = datetime.fromtimestamp(timestamp) if timestamp else None
        event_timestamp_proof = "0x" + timestamp_proof.hex() if timestamp_proof and isinstance(timestamp_proof,
                                                                                               bytes) else timestamp_proof
        raw_id = f"{doc_id}{external_hash}{sender}{time.time_ns()}"
        event_id = "0x" + hashlib.sha256(raw_id.encode()).hexdigest()
        self.event_repository.create(id=event_id, document_id=doc_id, metadata_text=metadata, sender=sender,
                                     origin=origin, hash=00000, external_hash=external_hash,
                                     timestamp_datetime=event_timestamp_datetime, timestamp_proof=event_timestamp_proof,
                                     timestamp_source="external" if event_timestamp_proof else "block")

    def _check_scope(self, current_user: User, method: str):
        """
        Checks if the current user has the necessary authorization to perform the
        specified method.

        :param current_user: The user object whose authorization is to be verified.
            Must provide sufficient privileges based on the method's scope
            requirements.
        :type current_user: User
        :param method: The name of the method for which the scope check is performed.
        :type method: str
        :return: None
        :raises TntServiceAuthError: If the user lacks authorization for the
            specified method.
        """
        is_authorized = check_scopes(current_user, method, {
            "authoriseDid": ["tnt_authorise"],
            "createDocument": ["tnt_create"],
            "removeDocument": ["tnt_write"],
            "grantAccess": ["tnt_write"],
            "revokeAccess": ["tnt_write"],
            "writeEvent": ["tnt_write"],
            "sendSignedTransaction": ["tnt_authorise", "tnt_create", "tnt_write"]
        })
        if not is_authorized:
            raise TntServiceAuthError("Forbidden method")

    def _check_did_access(self, current_user: User, payload: JsonRpcCreate):
        """
        Checks access permissions for a specific method and subject DID, ensuring the current user has
        the correct permissions.

        :param current_user: The user making the request.
        :type current_user: User
        :param payload: The payload of the JSON-RPC request containing method and parameters.
        :type payload: JsonRpcCreate
        :return: None
        :raises TntServiceRequestError: If the requested method is not allowed.
        :raises TntServiceAuthError: If the subject DID is present and does not match the current user's DID.
        """
        method = payload.method
        subject_did: str | None = payload.params[0].get("did", None) if len(payload.params) > 0 else None
        if method not in ("authoriseDid", "createDocument", "removeDocument", "grantAccess", "revokeAccess",
                          "writeEvent"):
            raise TntServiceRequestError("Method not allowed")

        if subject_did is not None and subject_did != current_user.sub:
            raise TntServiceAuthError("Forbidden DID")

    def _check_method_constraints(self, current_user: User, payload: JsonRpcCreate):
        """
        Checks constraints based on the provided `payload` method and validates access
        rights or input-related conditions for the operation to proceed.

        :param current_user: The currently authenticated user performing the action.
        :type current_user: User
        :param payload: The JSON-RPC payload containing method name and parameters for
                        the requested operation.
        :type payload: JsonRpcCreate
        :return: A validated and possibly modified set of parameters based on the
                 operation type.
        :rtype: dict
        :raises TntServiceRequestError: If constraints associated with the method
                                        are violated or parameters are invalid.
        :raises TntServiceNotFoundError: If the requested document is not found for
                                          relevant methods.
        :raises TntServiceAuthError: If the user lacks permissions required to perform
                                      the requested operation.
        """
        params = payload.params[0] if len(payload.params) > 0 else {}

        if payload.method == "authoriseDid":
            params['whiteList'] = booleanize(params['whiteList'])

        if payload.method == "createDocument":
            if "didEbsiCreator" in params and current_user.sub != params['didEbsiCreator']:
                raise TntServiceRequestError("didEbsiCreator is not the same as the subject")

        if payload.method == "removeDocument":
            document = self.get_document(params['eventParams'][0]['documentHash'])
            if document.creator != current_user.sub:
                raise TntServiceRequestError("Document creator is not the same as the subject")

        if payload.method == "grantAccess":
            if "grantedByAccount" in params and current_user.sub != params['grantedByAccount']:
                raise TntServiceRequestError("grantedByAccount is not the same as the subject")
            user_accesses = self.list_accesses(subject=params['grantedByAccount'],
                                               document_id=params['documentHash'])
            document = self.get_document(params['documentHash'])
            if document is None:
                raise TntServiceNotFoundError("Document not found")
            if document.creator != params['grantedByAccount']:
                if params['permission'] != PermissionEnum.write:
                    raise TntServiceRequestError("grantedByAccount is not the same as the creator")
                else:
                    is_delegated = bool(
                        [access for access in user_accesses if access.permission == PermissionEnum.delegate])
                    if not is_delegated:
                        raise TntServiceAuthError("Permission not granted")

        if payload.method == 'revokeAccess':
            if "revokedByAccount" in params and current_user.sub != params['revokedByAccount']:
                raise TntServiceRequestError("revokedByAccount is not the same as the subject")
            document = self.get_document(params['documentHash'])
            if document is None:
                raise TntServiceNotFoundError("Document not found")
            if document.creator != params['revokedByAccount']:
                raise TntServiceRequestError("revokedByAccount is not the same as the creator")

        if payload.method == "writeEvent":
            event_params = EventParams(**params['eventParams'][0])
            timestamp = int.from_bytes(
                bytes.fromhex(params['timestamp'].replace('0x', ''))) if 'timestamp' in params else None
            timestamp_proof = bytes.fromhex(
                params['timestampProof'].replace('0x', '')) if 'timestampProof' in params else None
            params = {'from': params['from'], 'eventParams': event_params}
            if timestamp:
                params['timestamp'] = timestamp
            if timestamp_proof:
                params['timestampProof'] = timestamp_proof
            document = self.get_document(event_params['documentHash'])
            user_accesses = [access for access in document.accesses if
                             access.subject == current_user.sub and access.permission == PermissionEnum.write]
            if document is None:
                raise TntServiceRequestError("Document not found")
            if document.creator != current_user.sub and len(user_accesses) == 0:
                raise TntServiceAuthError("Permission not granted")
            sender = event_params['sender'].decode('utf-8') if isinstance(event_params['sender'],
                                                                          bytes) else bytes.fromhex(
                event_params['sender'].replace('0x', '')).decode('utf-8')
            if sender != current_user.sub:
                raise TntServiceRequestError("Sender is not the same as the subject")
        return params

    def get_abi(self):
        """
        Retrieves the ABI (Application Binary Interface).

        The method fetches and returns the TNT's ABI.

        :return: The ABI associated with TNT.
        :rtype: dict
        """
        return self.tnt_abi

    def handle_rpc(self, current_user: User, payload: JsonRpcCreate):
        """
        Handles the RPC request by processing the method specified in the payload and taking appropriate actions.
        Supports creating or executing transactions based on the payload details.

        :param current_user: The user initiating the RPC request.
        :type current_user: User
        :param payload: The JSON-RPC payload containing method details and parameters.
        :type payload: JsonRpcCreate
        :return: The result of executing the JSON-RPC call, either an unsigned or a signed transaction.
        :rtype: dict
        :raises TntServiceError: If there is an internal error during processing.
        :raises EBSIError: Forwards any application-specific exceptions raised by the underlying methods.
        """
        try:
            params = payload.params[0] if len(payload.params) > 0 else {}
            self._check_scope(current_user, payload.method)
            if payload.method != "sendSignedTransaction":
                self._check_did_access(current_user, payload)
                params = self._check_method_constraints(current_user, payload)
                json_rpc_result = build_unsigned_transaction(self.eth_contract, settings.ETH_ADDRESS, payload.method,
                                                             params)
            else:
                json_rpc_result = exec_signed_transaction(current_user, self.eth_contract, settings.ETH_ADDRESS, self,
                                                          params['unsignedTransaction'],
                                                          params['signedRawTransaction'])
        except EBSIError:
            raise
        except Exception:
            raise TntServiceError("Internal error")
        else:
            return json_rpc_result
