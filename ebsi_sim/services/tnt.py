import hashlib
import json
import time
from datetime import datetime

from fastapi import Depends
from web3 import Web3
from web3.contract import Contract

from ebsi_sim.core.config import settings
from ebsi_sim.repositories.didr import IdentifierRepository
from ebsi_sim.repositories.tnt import AccessRepository
from ebsi_sim.repositories.tnt import DocumentRepository
from ebsi_sim.repositories.tnt import EventRepository
from ebsi_sim.schemas import JsonRpcCreate, PermissionEnum
from ebsi_sim.schemas.event import EventParams
from ebsi_sim.utils import check_scopes, User, build_unsigned_transaction, exec_signed_transaction, booleanize


class TntServiceException(Exception):
    pass

class TntService:
    eth_contract: type[Contract]
    document_repository: DocumentRepository
    access_repository: AccessRepository
    event_repository: EventRepository
    identifier_repository: IdentifierRepository

    def __init__(self, document_repository: DocumentRepository = Depends(),
                 access_repository: AccessRepository = Depends(), event_repository: EventRepository = Depends(),
                 identifier_repository: IdentifierRepository = Depends()):
        self.document_repository = document_repository
        self.access_repository = access_repository
        self.event_repository = event_repository
        self.identifier_repository = identifier_repository

        tnt_abi = json.load(open("ebsi_sim/includes/abi_tnt.json", "r"))
        self.eth_contract = Web3().eth.contract(abi=tnt_abi)

    def get_document(self, document_hash: bytes | str):
        if isinstance(document_hash, bytes):
            document_hash = "0x" + document_hash.hex()
        return self.document_repository.get(document_hash)

    def count_documents(self, **filters):
        return self.document_repository.count(**filters)

    def list_documents(self, *, offset=None, limit=None, order_by=None, **filters):
        return self.document_repository.list(offset=offset, limit=limit, order_by=order_by, **filters)

    def count_accesses(self, **filters):
        return self.access_repository.count(**filters)

    def list_accesses(self, *, offset=None, limit=None, order_by=None, **filters):
        return self.access_repository.list(offset=offset, limit=limit, order_by=order_by, **filters)

    def count_events(self, **filters):
        return self.event_repository.count(**filters)

    def list_events(self, *, offset=None, limit=None, order_by=None, **filters):
        return self.event_repository.list(offset=offset, limit=limit, order_by=order_by, **filters)

    def authorise_did(self, *, sender_did: str, authorised_did: str, white_list: bool):
        self.identifier_repository.update(id=authorised_did, tnt_authorized=white_list)

    def create_document(self, *, document_hash: bytes | str, document_metadata: str, did_ebsi_creator: str,
                       timestamp: int | None = None, timestamp_proof: bytes | str | None = None):
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
        if isinstance(document_hash, bytes):
            document_hash = "0x" + document_hash.hex()
        self.document_repository.delete(id=document_hash)

    def grant_access(self, *, document_hash: bytes | str, granted_by_account: bytes | str, subject_account: bytes | str, permission: str):
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

    def revoke_access(self, *, document_hash: bytes | str, revoked_by_account: bytes | str, subject_account: bytes | str, permission: str):
        if isinstance(document_hash, bytes):
            document_hash = "0x" + document_hash.hex()
        if isinstance(revoked_by_account, bytes):
            revoked_by_account = "0x" + revoked_by_account.hex()
        if isinstance(subject_account, bytes):
            subject_account = "0x" + subject_account.hex()
        permission = "write" if int(permission, 0) else "delegate"
        revoked_access = self.access_repository.list(subject=subject_account, document_id=document_hash, permission=permission)[
            0]
        self.access_repository.delete(id=revoked_access.id)


    def write_event(self, *, event_params: EventParams, timestamp: int | None = None, timestamp_proof: bytes | str | None = None):
        doc_id = "0x" + event_params['documentHash'].hex() if isinstance(event_params['documentHash'], bytes) else event_params['documentHash']
        external_hash = event_params['externalHash']
        sender = event_params['sender'].decode('utf-8') if isinstance(event_params['sender'], bytes) else event_params['sender']
        origin = event_params['origin']
        metadata = event_params['metadata']
        event_timestamp_datetime = datetime.fromtimestamp(timestamp) if timestamp else None
        event_timestamp_proof = "0x" + timestamp_proof.hex() if timestamp_proof and isinstance(timestamp_proof, bytes) else timestamp_proof
        raw_id = f"{doc_id}{external_hash}{sender}{time.time_ns()}"
        event_id = "0x" + hashlib.sha256(raw_id.encode()).hexdigest()
        self.event_repository.create(id=event_id, document_id=doc_id, metadata_text=metadata, sender=sender,
                                     origin=origin, hash=00000, external_hash=external_hash,
                                     timestamp_datetime=event_timestamp_datetime, timestamp_proof=event_timestamp_proof,
                                     timestamp_source="external" if event_timestamp_proof else "block")

    def _check_scope(self, current_user: User, method: str):
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
            raise TntServiceException("Forbidden method")

    def _check_did_access(self, current_user: User, payload: JsonRpcCreate):
        method = payload.method
        subject_did: str | None = payload.params[0].get("did", None) if len(payload.params) > 0 else None
        if method not in ("authoriseDid", "createDocument", "removeDocument", "grantAccess", "revokeAccess",
                          "writeEvent"):
            raise TntServiceException("Method not allowed")

    def _check_method_conditions(self, current_user: User, payload: JsonRpcCreate):
        params = payload.params[0] if len(payload.params) > 0 else {}

        if payload.method == "authoriseDid":
            params['whiteList'] = booleanize(params['whiteList'])

        if payload.method == "createDocument":
            if "didEbsiCreator" in params and current_user.sub != params['didEbsiCreator']:
                raise TntServiceException("didEbsiCreator is not the same as the subject")

        if payload.method == "removeDocument":
            document = self.get_document(params['eventParams'][0]['documentHash'])
            if document.creator != current_user.sub:
                raise TntServiceException("Document creator is not the same as the subject")

        if payload.method == "grantAccess":
            if "grantedByAccount" in params and current_user.sub != params['grantedByAccount']:
                raise TntServiceException("grantedByAccount is not the same as the subject")
            user_accesses = self.list_accesses(subject=params['grantedByAccount'],
                                                     document_id=params['documentHash'])
            document = self.get_document(params['documentHash'])
            if document is None:
                raise TntServiceException("Document not found")
            if document.creator != params['grantedByAccount']:
                if params['permission'] != PermissionEnum.write:
                    raise TntServiceException("grantedByAccount is not the same as the creator")
                else:
                    is_delegated = bool(
                        [access for access in user_accesses if access.permission == PermissionEnum.delegate])
                    if not is_delegated:
                        raise TntServiceException("Permission not granted")

        if payload.method == 'revokeAccess':
            if "revokedByAccount" in params and current_user.sub != params['revokedByAccount']:
                raise TntServiceException("revokedByAccount is not the same as the subject")
            document = self.get_document(params['documentHash'])
            if document is None:
                raise TntServiceException("Document not found")
            if document.creator != params['revokedByAccount']:
                raise TntServiceException("revokedByAccount is not the same as the creator")

        if payload.method == "writeEvent":
            event_params = EventParams(**params['eventParams'][0])
            timestamp = int.from_bytes(bytes.fromhex(params['timestamp'].replace('0x',''))) if 'timestamp' in params else None
            timestamp_proof = bytes.fromhex(params['timestampProof'].replace('0x', '')) if 'timestampProof' in params else None
            params = {'from': params['from'], 'eventParams': event_params}
            if timestamp:
                params['timestamp'] = timestamp
            if timestamp_proof:
                params['timestampProof'] = timestamp_proof
            document = self.get_document(event_params['documentHash'])
            user_accesses = [access for access in document.accesses if
                             access.subject == current_user.sub and access.permission == PermissionEnum.write]
            if document is None:
                raise TntServiceException("Document not found")
            if document.creator != current_user.sub and len(user_accesses) == 0:
                raise TntServiceException("Permission not granted")
            sender = event_params['sender'].decode('utf-8') if isinstance(event_params['sender'], bytes) else bytes.fromhex(event_params['sender'].replace('0x','')).decode('utf-8')
            if sender != current_user.sub:
                raise TntServiceException("Sender is not the same as the subject")
        return params

    def handle_rpc(self, current_user: User, payload: JsonRpcCreate):
        params = payload.params[0] if len(payload.params) > 0 else {}
        self._check_scope(current_user, payload.method)
        if payload.method != "sendSignedTransaction":
            self._check_did_access(current_user, payload)
            params = self._check_method_conditions(current_user, payload)
            json_rpc_result = build_unsigned_transaction(self.eth_contract, settings.ETH_ADDRESS, payload.method, params)
        else:
            json_rpc_result = exec_signed_transaction(current_user, self.eth_contract, settings.ETH_ADDRESS, self,
                                                      params['unsignedTransaction'],
                                                      params['signedRawTransaction'])
        return json_rpc_result