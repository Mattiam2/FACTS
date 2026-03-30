import hashlib
import time
from datetime import datetime

from fastapi import Depends

from ebsi_sim.repositories.didr import IdentifierRepository
from ebsi_sim.repositories.tnt import AccessRepository
from ebsi_sim.repositories.tnt import DocumentRepository
from ebsi_sim.repositories.tnt import EventRepository
from ebsi_sim.schemas.event import EventParams


class TntService:
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
