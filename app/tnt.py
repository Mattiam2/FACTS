from fastapi import Response, APIRouter
from typing import Annotated

from fastapi import FastAPI, Query
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, \
    HTTP_500_INTERNAL_SERVER_ERROR

from app.models import DocumentListResponse, DocumentItem, PageLinks, DocumentResponse, Timestamp, \
    EventListResponse, EventItem, EventResponse, AccessListResponse, AccessItem, JsonRPCModel, PermissionEnum, VersionEnum, \
    JsonRPCResponse

router = APIRouter(prefix="/track-and-trace", tags=["track-and-trace"])

@router.post("/jsonrpc", response_model=JsonRPCResponse)
async def rpc(payload: JsonRPCModel):
    return JsonRPCResponse(
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
async def check_access(creator: Annotated[str, Query()], ):
    return Response(status_code=HTTP_204_NO_CONTENT)

@router.get("/accesses", response_model=AccessListResponse)
async def read_doc_events(subject: str, page_after: Annotated[str, Query(alias="page[after]")] = None,
                    page_size: Annotated[str, Query(alias="page[size]")] = None):
    items = [
        AccessItem(subject=subject, documentId="doc1", grantedBy="admin", permission="write"),
        AccessItem(subject=subject, documentId="doc2", grantedBy="system", permission="creator"),
        AccessItem(subject=subject, documentId="doc3", grantedBy="admin", permission="delegate")
    ]

    links = PageLinks(first=f"/accesses?page[size]=10",
                      prev=f"/accesses?page[size]=10&page[after]=0",
                      next=f"/accesses?page[size]=10&page[after]=10",
                      last=f"/accesses?page[size]=10&page[after]=20")

    return AccessListResponse(
        self="/accesses",
        items=items,
        total=len(items),
        pageSize=10,
        links=links
    )


@router.get("/documents", response_model=DocumentListResponse)
async def read_docs(page_after: Annotated[str, Query(alias="page[after]")] = None,
                    page_size: Annotated[str, Query(alias="page[size]")] = None):
    items = [
        DocumentItem(documentId="doc1", href="/documents/doc1"),
        DocumentItem(documentId="doc2", href="/documents/doc2"),
        DocumentItem(documentId="doc3", href="/documents/doc3"),
        DocumentItem(documentId="doc4", href="/documents/doc4"),
        DocumentItem(documentId="doc5", href="/documents/doc5")
    ]

    links = PageLinks(first="/docuemnts?page[size]=10",
                      prev="/documents?page[size]=10&page[after]=0",
                      next="/documents?page[size]=10&page[after]=10",
                      last="/documents?page[size]=10&page[after]=20")

    return DocumentListResponse(
        self="/documents",
        items=items,
        total=len(items),
        pageSize=10,
        links=links
    )


@router.get("/documents/{documentId}", response_model=DocumentResponse)
async def read_doc(documentId: str, version: VersionEnum = VersionEnum.latest):
    timestamp = Timestamp(
        datetime="2025-11-25T12:00:00Z",
        source="system",
        proof="hash123456"
    )

    return DocumentResponse(
        metadata="Sample document metadata",
        timestamp=timestamp,
        creator="admin"
    )

@router.get("/documents/{documentId}/events", response_model=EventListResponse)
async def read_doc_events(documentId: str, page_after: Annotated[str, Query(alias="page[after]")] = None,
                    page_size: Annotated[str, Query(alias="page[size]")] = None):
    items = [
        EventItem(eventId="event1", href="/documents/doc1/events/event1"),
        EventItem(eventId="event2", href="/documents/doc1/events/event2"),
        EventItem(eventId="event3", href="/documents/doc1/events/event3")
    ]

    links = PageLinks(first=f"/documents/{documentId}/events?page[size]=10",
                      prev=f"/documents/{documentId}/events?page[size]=10&page[after]=0",
                      next=f"/documents/{documentId}/events?page[size]=10&page[after]=10",
                      last=f"/documents/{documentId}/events?page[size]=10&page[after]=20")

    return EventListResponse(
        self=f"/documents/{documentId}/events",
        items=items,
        total=len(items),
        pageSize=10,
        links=links
    )

@router.get("/documents/{documentId}/events/{eventId}", response_model=EventResponse)
async def read_doc_events(documentId: str, eventId: str):
    timestamp = Timestamp(
        datetime="2025-11-25T12:00:00Z",
        source="system",
        proof="hash123456"
    )

    return EventResponse(
        metadata="Sample event metadata",
        timestamp=timestamp,
        sender="system",
        origin="internal",
        hash="abc123def456",
        externalHash="xyz789"
    )

@router.get("/documents/{documentId}/accesses", response_model=AccessListResponse)
async def read_doc_events(documentId: str, page_after: Annotated[str, Query(alias="page[after]")] = None,
                    page_size: Annotated[str, Query(alias="page[size]")] = None):
    items = [
        AccessItem(subject="user1", documentId=documentId, grantedBy="admin", permission=PermissionEnum.write),
        AccessItem(subject="user2", documentId=documentId, grantedBy="admin", permission=PermissionEnum.delegate),
        AccessItem(subject="user3", documentId=documentId, grantedBy="system", permission=PermissionEnum.creator)
    ]

    links = PageLinks(first=f"/documents/{documentId}/accesses?page[size]=10",
                      prev=f"/documents/{documentId}/accesses?page[size]=10&page[after]=0",
                      next=f"/documents/{documentId}/accesses?page[size]=10&page[after]=10",
                      last=f"/documents/{documentId}/accesses?page[size]=10&page[after]=20")

    return AccessListResponse(
        self=f"/documents/{documentId}/accesses",
        items=items,
        total=len(items),
        pageSize=10,
        links=links
    )


@router.get("/abi")
async def abi():
    pass
