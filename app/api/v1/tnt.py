import math
from datetime import datetime

from fastapi import Response, APIRouter, Depends, HTTPException
from typing import Annotated

from fastapi import Query
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, \
    HTTP_500_INTERNAL_SERVER_ERROR

from app.core.db import db
from app.repositories.access import AccessRepository
from app.repositories.document import DocumentRepository
from app.repositories.event import EventRepository
from app.schemas.access import AccessItemPublic, AccessListPublic
from app.schemas.document import DocumentItemPublic, DocumentListPublic, DocumentPublic
from app.schemas.event import EventItemPublic, EventListPublic, EventPublic
from app.schemas.jsonrpc import JsonRpcCreate, JsonRpcPublic
from app.schemas.shared import PageLinksPublic, TimestampPublic, VersionEnum

router = APIRouter(prefix="/track-and-trace", tags=["track-and-trace"])


@router.post("/jsonrpc")
async def rpc(payload: JsonRpcCreate) -> JsonRpcPublic:
    match payload.method:
        case "authoriseDid":
            pass
        case "createDocument":
            doc_repo = DocumentRepository()
            docs_params = payload.params
            for doc in docs_params:
                doc_id = doc['documentHash']
                doc_metadata_hex = doc['documentMetadata'][2:]
                doc_metadata = bytes.fromhex(doc_metadata_hex).decode('utf-8')
                doc_creator = doc['didEbsiCreator']
                doc_timestamp_datetime_hex = doc['timestamp'] if 'timestamp' in doc else None
                doc_timestamp_datetime = datetime.fromtimestamp(int(doc_timestamp_datetime_hex, 0)) if doc_timestamp_datetime_hex else None
                doc_timestamp_proof = doc['timestampProof'] if 'timestampProof' in doc else None
                doc_repo.create(commit=False, id=doc_id, creator=doc_creator, metadata_text=doc_metadata,
                                timestamp_datetime=doc_timestamp_datetime, timestamp_proof=doc_timestamp_proof,
                                timestamp_source="block")
            db.session.commit()
        case "removeDocument":
            doc_repo = DocumentRepository()
            docs_params = payload.params
            for doc in docs_params:
                doc_id = doc['documentHash']
                #eth_from = doc['from']
                doc_repo.delete(commit=False, id=doc_id)
            db.session.commit()
        case "grantAccess":
            access_repo = AccessRepository()
            access_params = payload.params
            for access in access_params:
                doc_id = access['documentHash']
                # eth_from = access['from']
                granted_by_hex = access['grantedByAccount'][2:]
                granted_by = bytes.fromhex(granted_by_hex).decode('utf-8')
                subject_hex = access['subjectAccount'][2:]
                subject = bytes.fromhex(subject_hex).decode('utf-8')
                #granted_by_type = access['grantedByAccType']
                #subject_type = access['subjectAccType']
                permission = access['permission']
                access_repo.create(commit=False, subject=subject, document_id=doc_id, granted_by=granted_by, permission=permission)
            db.session.commit()
        case "revokeAccess":
            access_repo = AccessRepository()
            access_params = payload.params
            for access in access_params:
                doc_id = access['documentHash']
                revoked_by_hex = access['revokedByAccount'][2:]
                revoked_by = bytes.fromhex(revoked_by_hex).decode('utf-8')
                subject_hex = access['subjectAccount'][2:]
                subject = bytes.fromhex(subject_hex).decode('utf-8')
                permission = access['permission']
                revoked_access = access_repo.list(subject=subject, document_id=doc_id, permission=permission)[0]
                access_repo.delete(commit=False, id=revoked_access.id)
            db.session.commit()
        case "writeEvent":
            event_repo = EventRepository()
            event_params = payload.params
            for event in event_params:
                doc_id = event['eventParams'][0]['documentHash']
                external_hash = event['eventParams'][0]['externalHash']
                sender_hex = event['eventParams'][0]['sender'][2:]
                sender = bytes.fromhex(sender_hex).decode('utf-8')
                origin = event['eventParams'][0]['origin']
                metadata = event['eventParams'][0]['metadata']
                event_timestamp_datetime_hex = event['timestamp'] if 'timestamp' in event else None
                event_timestamp_datetime = datetime.fromtimestamp(
                    int(event_timestamp_datetime_hex, 0)) if event_timestamp_datetime_hex else None
                event_timestamp_proof = event['timestampProof'] if 'timestampProof' in event else None
                event_repo.create(commit=False, document_id=doc_id, metadata_text=metadata, sender=sender, origin=origin, hash=00000, external_hash=external_hash, timestamp_datetime=event_timestamp_datetime, timestamp_proof=event_timestamp_proof, timestamp_source="block")
            db.session.commit()
        case "sendSignedTransaction":
            pass
        case _:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid method")

    return JsonRpcPublic(
        jsonrpc="2.0",
        id=payload.id,
        result={"status": "success", "message": "Operation completed successfully"}
    )


@router.head("/accesses", responses={
    HTTP_204_NO_CONTENT: {"description": "Success"},
    HTTP_400_BAD_REQUEST: {"description": "Bad Request Error"},
    HTTP_404_NOT_FOUND: {"description": "DID not found in the allowlist"},
    HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"}
})
async def check_access(creator: Annotated[str, Query()]):
    access_repo = AccessRepository()
    creator_access = access_repo.list(subject=creator)

    if not creator_access:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="DID not found in the allowlist")

    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get("/accesses")
async def read_subject_accesses(subject: str, page_after: Annotated[int, Query(alias="page[after]")] = 1,
                                page_size: Annotated[int, Query(alias="page[size]")] = 10) -> AccessListPublic:
    access_repo = AccessRepository()

    accesses_count = access_repo.count(subject=subject)
    n_pages = math.ceil(accesses_count / page_size)

    links = PageLinksPublic(first=f"/accesses?page[after]=1&page[size]={page_size}&subject={subject}",
                            prev=f"/accesses?page[after]={max(1, page_after - 1)}&page[size]={page_size}&subject={subject}",
                            next=f"/accesses?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}&subject={subject}",
                            last=f"/accesses?page[after]={max(n_pages, 1)}&page[size]={page_size}&subject={subject}")

    accesses = access_repo.list(offset=(page_after - 1) * page_size, limit=page_size, subject=subject)

    return AccessListPublic(
        self=f"/accesses?page[after]={page_after}&page[size]={page_size}&subject={subject}",
        items=accesses,
        total=accesses_count,
        pageSize=page_size,
        links=links
    )


@router.get("/documents")
async def read_docs(page_after: Annotated[int, Query(alias="page[after]")] = 1,
                    page_size: Annotated[int, Query(alias="page[size]")] = 10) -> DocumentListPublic:
    doc_repo = DocumentRepository()
    docs_count = doc_repo.count()
    n_pages = math.ceil(docs_count / page_size)

    links = PageLinksPublic(first=f"/documents?page[after]=1&page[size]={page_size}",
                            prev=f"/documents?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/documents?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/documents?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    docs = doc_repo.list(offset=(page_after - 1) * page_size, limit=page_size)
    items = []
    for doc in docs:
        items.append(DocumentItemPublic(documentId=doc.id, href=f"/documents/{doc.id}"))

    return DocumentListPublic(
        self=f"/documents?page[after]={page_after}&page[size]={page_size}",
        items=items,
        total=docs_count,
        pageSize=page_size,
        links=links
    )


@router.get("/documents/{documentId}")
async def read_doc(documentId: str, version: VersionEnum = VersionEnum.latest) -> DocumentPublic:
    doc_repo = DocumentRepository()

    doc = doc_repo.get(documentId)

    timestamp = TimestampPublic(
        datetime=doc.timestamp_datetime.isoformat(),
        source=doc.timestamp_source,
        proof=doc.timestamp_proof
    )

    return DocumentPublic(
        metadata_text=doc.metadata_text,
        timestamp=timestamp,
        creator=doc.creator
    )


@router.get("/documents/{documentId}/events")
async def read_doc_events(documentId: str, page_after: Annotated[int, Query(alias="page[after]")] = 1,
                          page_size: Annotated[int, Query(alias="page[size]")] = 10) -> EventListPublic:
    event_repo = EventRepository()
    events_count = event_repo.count(document_id=documentId)
    n_pages = math.ceil(events_count / page_size)

    links = PageLinksPublic(first=f"/documents/{documentId}/events?page[after]=1&page[size]={page_size}",
                            prev=f"/documents/{documentId}/events?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/documents/{documentId}/events?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/documents/{documentId}/events?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    events = event_repo.list(offset=(page_after - 1) * page_size, limit=page_size, document_id=documentId)

    items = []
    for event in events:
        items.append(EventItemPublic(eventId=event.id, href=f"/documents/{documentId}/events/{event.id}"))

    return EventListPublic(
        self=f"/documents/{documentId}/events?page[after]={page_after}&page[size]={page_size}",
        items=items,
        total=events_count,
        pageSize=page_size,
        links=links
    )


@router.get("/documents/{documentId}/events/{eventId}")
async def read_doc_event(documentId: str, eventId: str) -> EventPublic:
    event_repo = EventRepository()

    events = event_repo.list(id=eventId, document_id=documentId)
    event = events[0] if events else None

    timestamp = TimestampPublic(
        datetime=event.timestamp_datetime.isoformat(),
        source=event.timestamp_source,
        proof=event.timestamp_proof
    )

    event_public = EventPublic(**event.dict(), timestamp=timestamp)

    return event_public


@router.get("/documents/{documentId}/accesses")
async def read_doc_accesses(documentId: str, page_after: Annotated[int, Query(alias="page[after]")] = 1,
                            page_size: Annotated[int, Query(alias="page[size]")] = 10) -> AccessListPublic:
    access_repo = AccessRepository()

    accesses_count = access_repo.count(document_id=documentId)
    n_pages = math.ceil(accesses_count / page_size)

    links = PageLinksPublic(first=f"/documents/{documentId}/accesses?page[after]=1&page[size]={page_size}",
                            prev=f"/documents/{documentId}/accesses?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/documents/{documentId}/accesses?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/documents/{documentId}/accesses?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    accesses = access_repo.list(document_id=documentId, offset=(page_after - 1) * page_size, limit=page_size)

    return AccessListPublic(
        self=f"/documents/{documentId}/accesses?page[after]={page_after}&page[size]={page_size}&documentId={documentId}",
        items=accesses,
        total=accesses_count,
        pageSize=page_size,
        links=links
    )


@router.get("/abi")
async def abi():
    pass
