import hashlib
import time
import uuid
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

    def getDocument(self, documentHash: bytes | str):
        if isinstance(documentHash, bytes):
            documentHash = "0x" + documentHash.hex()
        return self.document_repository.get(documentHash)

    def countDocuments(self, **filters):
        return self.document_repository.count(**filters)

    def listDocuments(self, *, offset=None, limit=None, order_by=None, **filters):
        return self.document_repository.list(offset=offset, limit=limit, order_by=order_by, **filters)

    def countAccesses(self, **filters):
        return self.access_repository.count(**filters)

    def listAccesses(self, *, offset=None, limit=None, order_by=None, **filters):
        return self.access_repository.list(offset=offset, limit=limit, order_by=order_by, **filters)

    def countEvents(self, **filters):
        return self.event_repository.count(**filters)

    def listEvents(self, *, offset=None, limit=None, order_by=None, **filters):
        return self.event_repository.list(offset=offset, limit=limit, order_by=order_by, **filters)

    def authoriseDid(self, *, senderDid: str, authorisedDid: str, whiteList: bool):
        self.identifier_repository.update(id=authorisedDid, tnt_authorized=whiteList)

    def createDocument(self, *, documentHash: bytes | str, documentMetadata: str, didEbsiCreator: str,
                       timestamp: int | None = None, timestampProof: bytes | str | None = None):
        doc_metadata = bytes.fromhex(documentMetadata[2:]).decode('utf-8')
        doc_timestamp_datetime = datetime.fromtimestamp(timestamp) if timestamp else None
        doc_timestamp_proof = timestampProof

        if isinstance(documentHash, bytes):
            documentHash = "0x" + documentHash.hex()

        if doc_timestamp_proof and isinstance(doc_timestamp_proof, bytes):
            doc_timestamp_proof = "0x" + doc_timestamp_proof.hex()

        self.document_repository.create(id=documentHash, creator=didEbsiCreator,
                                        metadata_text=doc_metadata,
                                        timestamp_datetime=doc_timestamp_datetime, timestamp_proof=doc_timestamp_proof,
                                        timestamp_source="external" if doc_timestamp_proof else "block")

    def removeDocument(self, *, documentHash: bytes | str):
        if isinstance(documentHash, bytes):
            documentHash = "0x" + documentHash.hex()
        self.document_repository.delete(id=documentHash)

    def grantAccess(self, *, documentHash: bytes | str, grantedByAccount: bytes | str, subjectAccount: bytes | str, permission: str):
        if isinstance(documentHash, bytes):
            documentHash = "0x" + documentHash.hex()
        if isinstance(grantedByAccount, bytes):
            grantedByAccount = "0x" + grantedByAccount.hex()
        if isinstance(subjectAccount, bytes):
            subjectAccount = "0x" + subjectAccount.hex()
        # granted_by_type = access['grantedByAccType']
        # subject_type = access['subjectAccType']
        permission = "write" if int(permission, 0) else "delegate"
        self.access_repository.create(subject=subjectAccount, document_id=documentHash, granted_by=grantedByAccount,
                                      permission=permission)

    def revokeAccess(self, *, documentHash: bytes | str, revokedByAccount: bytes | str, subjectAccount: bytes | str, permission: str):
        if isinstance(documentHash, bytes):
            documentHash = "0x" + documentHash.hex()
        if isinstance(revokedByAccount, bytes):
            revokedByAccount = "0x" + revokedByAccount.hex()
        if isinstance(subjectAccount, bytes):
            subjectAccount = "0x" + subjectAccount.hex()
        permission = "write" if int(permission, 0) else "delegate"
        revoked_access = self.access_repository.list(subject=subjectAccount, document_id=documentHash, permission=permission)[
            0]
        self.access_repository.delete(id=revoked_access.id)


    def writeEvent(self, *, eventParams: EventParams, timestamp: int | None = None, timestampProof: bytes | str | None = None):
        doc_id = "0x" + eventParams['documentHash'].hex() if isinstance(eventParams['documentHash'], bytes) else eventParams['documentHash']
        external_hash = eventParams['externalHash']
        sender = eventParams['sender'].decode('utf-8') if isinstance(eventParams['sender'], bytes) else eventParams['sender']
        origin = eventParams['origin']
        metadata = eventParams['metadata']
        event_timestamp_datetime = datetime.fromtimestamp(timestamp) if timestamp else None
        event_timestamp_proof = "0x" + timestampProof.hex() if timestampProof and isinstance(timestampProof, bytes) else timestampProof
        raw_id = f"{doc_id}{external_hash}{sender}{time.time_ns()}"
        event_id = "0x" + hashlib.sha256(raw_id.encode()).hexdigest()
        self.event_repository.create(id=event_id, document_id=doc_id, metadata_text=metadata, sender=sender,
                                     origin=origin, hash=00000, external_hash=external_hash,
                                     timestamp_datetime=event_timestamp_datetime, timestamp_proof=event_timestamp_proof,
                                     timestamp_source="external" if event_timestamp_proof else "block")
