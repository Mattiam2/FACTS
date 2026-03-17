from datetime import datetime

from fastapi import Depends

from ebsi_sim.core.db import db
from ebsi_sim.repositories.didr import IdentifierRepository
from ebsi_sim.repositories.tnt import AccessRepository
from ebsi_sim.repositories.tnt import DocumentRepository
from ebsi_sim.repositories.tnt import EventRepository

class TntService:
    document_repository: DocumentRepository
    access_repository: AccessRepository
    event_repository: EventRepository
    identifier_repository: IdentifierRepository

    def __init__(self, document_repository: DocumentRepository = Depends(), access_repository: AccessRepository = Depends(), event_repository: EventRepository = Depends(), identifier_repository: IdentifierRepository = Depends()):
        self.document_repository = document_repository
        self.access_repository = access_repository
        self.event_repository = event_repository
        self.identifier_repository = identifier_repository

    def getDocument(self, documentHash: str):
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

    def createDocument(self, *, documentHash: str, documentMetadata: str, didEbsiCreator: str, timestamp: str | None = None, timestampProof: str | None = None):
        doc_metadata = bytes.fromhex(documentMetadata[2:]).decode('utf-8')
        doc_timestamp_datetime = datetime.fromtimestamp(
            int(timestamp, 0)) if timestamp is not None else None
        doc_timestamp_proof = timestampProof
        self.document_repository.create(commit=False, id=documentHash, creator=didEbsiCreator, metadata_text=doc_metadata,
                        timestamp_datetime=doc_timestamp_datetime, timestamp_proof=doc_timestamp_proof,
                        timestamp_source="block")
        db.session.commit()

    def removeDocument(self, *, documentHash: bytes):
        document_hash_str = documentHash.decode('utf-8')
        self.document_repository.delete(commit=False, id=document_hash_str)
        db.session.commit()


    def grantAccess(self, *, documentHash: str, grantedByAccount: str, subjectAccount: str, permission: str):
        granted_by = bytes.fromhex(grantedByAccount[2:]).decode('utf-8')
        subject = bytes.fromhex(subjectAccount[2:]).decode('utf-8')
        # granted_by_type = access['grantedByAccType']
        # subject_type = access['subjectAccType']
        permission = "write" if int(permission, 0) else "delegate"
        self.access_repository.create(commit=False, subject=subject, document_id=documentHash, granted_by=granted_by,
                           permission=permission)
        db.session.commit()


    def revokeAccess(self, *, documentHash: str, revokedByAccount: str, subjectAccount: str, permission: str):
        revoked_by = bytes.fromhex(revokedByAccount[2:]).decode('utf-8')
        subject = bytes.fromhex(subjectAccount[2:]).decode('utf-8')
        permission = "write" if int(permission, 0) else "delegate"
        revoked_access = self.access_repository.list(subject=subject, document_id=documentHash, permission=permission)[0]
        self.access_repository.delete(commit=False, id=revoked_access.id)
        db.session.commit()


    def writeEvent(self, *, eventParams: list[dict], timestamp: str | None = None, timestampProof: str | None = None):
        doc_id = eventParams[0]['documentHash']
        external_hash = eventParams[0]['externalHash']
        sender = bytes.fromhex(eventParams[0]['sender'][2:]).decode('utf-8')
        origin = eventParams[0]['origin']
        metadata = eventParams[0]['metadata']
        event_timestamp_datetime = datetime.fromtimestamp(
            int(timestamp, 0)) if timestamp else None
        event_timestamp_proof = timestampProof
        self.event_repository.create(commit=False, document_id=doc_id, metadata_text=metadata, sender=sender,
                          origin=origin, hash=00000, external_hash=external_hash,
                          timestamp_datetime=event_timestamp_datetime, timestamp_proof=event_timestamp_proof,
                          timestamp_source="block")
        db.session.commit()