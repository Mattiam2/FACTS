from datetime import datetime

from ebsi_sim.core.db import db
from ebsi_sim.repositories.access import AccessRepository
from ebsi_sim.repositories.document import DocumentRepository
from ebsi_sim.repositories.event import EventRepository


def createDocument(documentHash: str, documentMetadata: str, didEbsiCreator: str, timestamp: str | None = None, timestampProof: str | None = None):
    doc_repo = DocumentRepository()
    doc_metadata = bytes.fromhex(documentMetadata[2:]).decode('utf-8')
    doc_timestamp_datetime = datetime.fromtimestamp(
        int(timestamp, 0)) if timestamp is not None else None
    doc_timestamp_proof = timestampProof
    doc_repo.create(commit=False, id=documentHash, creator=didEbsiCreator, metadata_text=doc_metadata,
                    timestamp_datetime=doc_timestamp_datetime, timestamp_proof=doc_timestamp_proof,
                    timestamp_source="block")
    db.session.commit()


def removeDocument(documentHash: bytes):
    doc_repo = DocumentRepository()
    document_hash_str = documentHash.decode('utf-8')
    doc_repo.delete(commit=False, id=document_hash_str)
    db.session.commit()


def grantAccess(documentHash: str, grantedByAccount: str, subjectAccount: str, permission: str):
    access_repo = AccessRepository()
    granted_by = bytes.fromhex(grantedByAccount[2:]).decode('utf-8')
    subject = bytes.fromhex(subjectAccount[2:]).decode('utf-8')
    # granted_by_type = access['grantedByAccType']
    # subject_type = access['subjectAccType']
    permission = "write" if int(permission, 0) else "delegate"
    access_repo.create(commit=False, subject=subject, document_id=documentHash, granted_by=granted_by,
                       permission=permission)
    db.session.commit()


def revokeAccess(documentHash: str, revokedByAccount: str, subjectAccount: str, permission: str):
    access_repo = AccessRepository()
    revoked_by = bytes.fromhex(revokedByAccount[2:]).decode('utf-8')
    subject = bytes.fromhex(subjectAccount[2:]).decode('utf-8')
    permission = "write" if int(permission, 0) else "delegate"
    revoked_access = access_repo.list(subject=subject, document_id=documentHash, permission=permission)[0]
    access_repo.delete(commit=False, id=revoked_access.id)
    db.session.commit()


def writeEvent(eventParams: list[dict], timestamp: str | None = None, timestampProof: str | None = None):
    event_repo = EventRepository()
    doc_id = eventParams[0]['documentHash']
    external_hash = eventParams[0]['externalHash']
    sender = bytes.fromhex(eventParams[0]['sender'][2:]).decode('utf-8')
    origin = eventParams[0]['origin']
    metadata = eventParams[0]['metadata']
    event_timestamp_datetime = datetime.fromtimestamp(
        int(timestamp, 0)) if timestamp else None
    event_timestamp_proof = timestampProof
    event_repo.create(commit=False, document_id=doc_id, metadata_text=metadata, sender=sender,
                      origin=origin, hash=00000, external_hash=external_hash,
                      timestamp_datetime=event_timestamp_datetime, timestamp_proof=event_timestamp_proof,
                      timestamp_source="block")
    db.session.commit()