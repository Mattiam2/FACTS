import math

from fastapi import Response, APIRouter, Depends
from typing import Annotated

from fastapi import Query
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, \
    HTTP_500_INTERNAL_SERVER_ERROR

from app.repositories.document import DocumentRepository
from app.schemas.access import AccessItemPublic, AccessListPublic
from app.schemas.document import DocumentItemPublic, DocumentListPublic, DocumentPublic
from app.schemas.event import EventItemPublic, EventListPublic, EventPublic
from app.schemas.jsonrpc import JsonRpcCreate, JsonRpcPublic
from app.schemas.shared import PageLinksPublic, TimestampPublic, VersionEnum

router = APIRouter(prefix="/track-and-trace", tags=["track-and-trace"])

@router.post("/jsonrpc")
async def rpc(payload: JsonRpcCreate) -> JsonRpcPublic:
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
    return Response(status_code=HTTP_204_NO_CONTENT)

@router.get("/accesses")
async def read_doc_events(subject: str, page_after: Annotated[str, Query(alias="page[after]")] = None,
                    page_size: Annotated[str, Query(alias="page[size]")] = None) -> AccessListPublic:
    items = [
        AccessItemPublic(subject=subject, documentId="doc1", grantedBy="admin", permission="write"),
        AccessItemPublic(subject=subject, documentId="doc2", grantedBy="system", permission="creator"),
        AccessItemPublic(subject=subject, documentId="doc3", grantedBy="admin", permission="delegate")
    ]

    links = PageLinksPublic(first=f"/accesses?page[size]=10",
                            prev=f"/accesses?page[size]=10&page[after]=0",
                            next=f"/accesses?page[size]=10&page[after]=10",
                            last=f"/accesses?page[size]=10&page[after]=20")

    return AccessListPublic(
        self="/accesses",
        items=items,
        total=len(items),
        pageSize=10,
        links=links
    )


@router.get("/documents")
async def read_docs(doc_repo: DocumentRepository = Depends(), page_after: Annotated[int, Query(alias="page[after]")] = 1,
                    page_size: Annotated[int, Query(alias="page[size]")] = 10) -> DocumentListPublic:
    items = []
    docs_count = doc_repo.count()
    n_pages = math.ceil(docs_count/page_size)

    links = PageLinksPublic(first=f"/documents?page[after]=1&page[size]={page_size}",
                            prev=f"/documents?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/documents?page[after]={max(1, page_after + 1, math.ceil(docs_count/page_size))}&page[size]={page_size}",
                            last="/documents?page[size]=10&page[after]=20")

    docs = doc_repo.list(offset=(page_after - 1) * page_size, limit=page_size)
    for doc in docs:
        items.append(DocumentItemPublic(documentId=doc.id, href=f"/documents/{doc.id}"))

    return DocumentListPublic(
        self="/documents",
        items=items,
        total=len(items),
        pageSize=page_size,
        links=links
    )


@router.get("/documents/{documentId}")
async def read_doc(documentId: str, version: VersionEnum = VersionEnum.latest) -> DocumentPublic:
    timestamp = TimestampPublic(
        datetime="2025-11-25T12:00:00Z",
        source="system",
        proof="hash123456"
    )

    return DocumentPublic(
        metadata_json="Sample document metadata",
        timestamp=timestamp,
        creator="admin"
    )

@router.get("/documents/{documentId}/events")
async def read_doc_events(documentId: str, page_after: Annotated[str, Query(alias="page[after]")] = None,
                    page_size: Annotated[str, Query(alias="page[size]")] = None) -> EventListPublic:
    items = [
        EventItemPublic(eventId="event1", href="/documents/doc1/events/event1"),
        EventItemPublic(eventId="event2", href="/documents/doc1/events/event2"),
        EventItemPublic(eventId="event3", href="/documents/doc1/events/event3")
    ]

    links = PageLinksPublic(first=f"/documents/{documentId}/events?page[size]=10",
                            prev=f"/documents/{documentId}/events?page[size]=10&page[after]=0",
                            next=f"/documents/{documentId}/events?page[size]=10&page[after]=10",
                            last=f"/documents/{documentId}/events?page[size]=10&page[after]=20")

    return EventListPublic(
        self=f"/documents/{documentId}/events",
        items=items,
        total=len(items),
        pageSize=10,
        links=links
    )

@router.get("/documents/{documentId}/events/{eventId}")
async def read_doc_event(documentId: str, eventId: str) -> EventPublic:
    timestamp = TimestampPublic(
        datetime="2025-11-25T12:00:00Z",
        source="system",
        proof="hash123456"
    )

    return EventPublic(
        metadata_json="Sample event metadata",
        timestamp=timestamp,
        sender="system",
        origin="internal",
        hash="abc123def456",
        externalHash="xyz789"
    )

@router.get("/documents/{documentId}/accesses")
async def read_doc_accesses(documentId: str, page_after: Annotated[str, Query(alias="page[after]")] = None,
                    page_size: Annotated[str, Query(alias="page[size]")] = None) -> AccessListPublic:
    items = [
        AccessItemPublic(subject="user1", documentId=documentId, grantedBy="admin", permission=PermissionEnum.write),
        AccessItemPublic(subject="user2", documentId=documentId, grantedBy="admin", permission=PermissionEnum.delegate),
        AccessItemPublic(subject="user3", documentId=documentId, grantedBy="system", permission=PermissionEnum.creator)
    ]

    links = PageLinksPublic(first=f"/documents/{documentId}/accesses?page[size]=10",
                            prev=f"/documents/{documentId}/accesses?page[size]=10&page[after]=0",
                            next=f"/documents/{documentId}/accesses?page[size]=10&page[after]=10",
                            last=f"/documents/{documentId}/accesses?page[size]=10&page[after]=20")

    return AccessListPublic(
        self=f"/documents/{documentId}/accesses",
        items=items,
        total=len(items),
        pageSize=10,
        links=links
    )


@router.get("/abi")
async def abi():
    pass
