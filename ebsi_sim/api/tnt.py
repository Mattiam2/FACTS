import json
import math
from typing import Annotated

from fastapi import Query
from fastapi import Response, APIRouter, Depends, HTTPException
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, \
    HTTP_500_INTERNAL_SERVER_ERROR
from web3 import Web3

from ebsi_sim.schemas import AccessListPublic, DocumentItemPublic, DocumentListPublic, DocumentPublic, EventItemPublic, \
    EventListPublic, EventPublic, JsonRpcCreate, JsonRpcPublic, PageLinksPublic, TimestampPublic, VersionEnum
from ebsi_sim.services.tnt import TntService
from ebsi_sim.utils import User, get_current_user

w3 = Web3()
router = APIRouter(prefix="/track-and-trace", tags=["track-and-trace"])


@router.post("/jsonrpc",
             description="The JSON-RPC API provides methods assisting the construction of blockchain transactions and interaction with the ledger, i.e. write operation on ledger.")
def rpc(current_user: Annotated[User, Depends(get_current_user)], payload: JsonRpcCreate,
        tnt_service: TntService = Depends()) -> JsonRpcPublic:
    json_rpc_result = tnt_service.handle_rpc(current_user, payload)

    return JsonRpcPublic(
        jsonrpc="2.0",
        id=payload.id,
        result=json_rpc_result
    )


@router.head("/accesses", description="Checks if the DID is included in the allowlist of TnT Document creators or not.",
             responses={
                 HTTP_204_NO_CONTENT: {"description": "Success"},
                 HTTP_400_BAD_REQUEST: {"description": "Bad Request Error"},
                 HTTP_404_NOT_FOUND: {"description": "DID not found in the allowlist"},
                 HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
             })
def check_access(creator: Annotated[str, Query()], tnt_service: TntService = Depends()):
    creator_access = tnt_service.list_accesses(subject=creator)

    if not creator_access:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="DID not found in the allowlist")

    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get("/accesses", description="Get accesses filtered by subject.")
def read_subject_accesses(subject: str, page_after: Annotated[int, Query(alias="page[after]")] = 1,
                          page_size: Annotated[int, Query(alias="page[size]")] = 10,
                          tnt_service: TntService = Depends()) -> AccessListPublic:
    accesses_count = tnt_service.count_accesses(subject=subject)
    n_pages = math.ceil(accesses_count / page_size)

    links = PageLinksPublic(first=f"/accesses?page[after]=1&page[size]={page_size}&subject={subject}",
                            prev=f"/accesses?page[after]={max(1, page_after - 1)}&page[size]={page_size}&subject={subject}",
                            next=f"/accesses?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}&subject={subject}",
                            last=f"/accesses?page[after]={max(n_pages, 1)}&page[size]={page_size}&subject={subject}")

    accesses = tnt_service.list_accesses(offset=(page_after - 1) * page_size, limit=page_size, subject=subject)

    return AccessListPublic(
        self=f"/accesses?page[after]={page_after}&page[size]={page_size}&subject={subject}",
        items=accesses,
        total=accesses_count,
        pageSize=page_size,
        links=links
    )


@router.get("/documents", description="Returns a list of documents.")
def read_docs(page_after: Annotated[int, Query(alias="page[after]")] = 1,
              page_size: Annotated[int, Query(alias="page[size]")] = 10,
              tnt_service: TntService = Depends()) -> DocumentListPublic:
    docs_count = tnt_service.count_documents()
    n_pages = math.ceil(docs_count / page_size)

    links = PageLinksPublic(first=f"/documents?page[after]=1&page[size]={page_size}",
                            prev=f"/documents?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/documents?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/documents?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    docs = tnt_service.list_documents(offset=(page_after - 1) * page_size, limit=page_size)
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


@router.get("/documents/{documentId}", description="Gets the document corresponding to the ID.")
def read_doc(documentId: str, version: VersionEnum = VersionEnum.latest,
             tnt_service: TntService = Depends()) -> DocumentPublic:
    doc = tnt_service.get_document(documentId)

    timestamp = TimestampPublic(
        datetime=doc.timestamp_datetime.isoformat() if doc.timestamp_datetime else None,
        source=doc.timestamp_source,
        proof=doc.timestamp_proof
    )

    return DocumentPublic(
        metadata_text=doc.metadata_text,
        timestamp=timestamp,
        creator=doc.creator
    )


@router.get("/documents/{documentId}/events", description="Returns a list of events.")
def read_doc_events(documentId: str, page_after: Annotated[int, Query(alias="page[after]")] = 1,
                    page_size: Annotated[int, Query(alias="page[size]")] = 10,
                    tnt_service: TntService = Depends()) -> EventListPublic:
    events_count = tnt_service.count_events(document_id=documentId)
    n_pages = math.ceil(events_count / page_size)

    links = PageLinksPublic(first=f"/documents/{documentId}/events?page[after]=1&page[size]={page_size}",
                            prev=f"/documents/{documentId}/events?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/documents/{documentId}/events?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/documents/{documentId}/events?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    events = tnt_service.list_events(offset=(page_after - 1) * page_size, limit=page_size, document_id=documentId)

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


@router.get("/documents/{documentId}/events/{eventId}",
            description="Gets the event corresponding to the document ID and event ID.")
def read_doc_event(documentId: str, eventId: str, tnt_service: TntService = Depends()) -> EventPublic:
    events = tnt_service.list_events(document_id=documentId, id=eventId)
    if not events:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Event not found")
    event = events[0]

    timestamp = TimestampPublic(
        datetime=event.timestamp_datetime.isoformat() if event.timestamp_datetime else None,
        source=event.timestamp_source,
        proof=event.timestamp_proof
    )

    event_public = EventPublic(**event.model_dump(), timestamp=timestamp)

    return event_public


@router.get("/documents/{documentId}/accesses", description="Returns a list of accesses related to the document.")
def read_doc_accesses(documentId: str, page_after: Annotated[int, Query(alias="page[after]")] = 1,
                      page_size: Annotated[int, Query(alias="page[size]")] = 10,
                      tnt_service: TntService = Depends()) -> AccessListPublic:
    accesses_count = tnt_service.count_accesses(document_id=documentId)
    n_pages = math.ceil(accesses_count / page_size)

    links = PageLinksPublic(first=f"/documents/{documentId}/accesses?page[after]=1&page[size]={page_size}",
                            prev=f"/documents/{documentId}/accesses?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/documents/{documentId}/accesses?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/documents/{documentId}/accesses?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    accesses = tnt_service.list_accesses(document_id=documentId, offset=(page_after - 1) * page_size, limit=page_size)

    return AccessListPublic(
        self=f"/documents/{documentId}/accesses?page[after]={page_after}&page[size]={page_size}&documentId={documentId}",
        items=accesses,
        total=accesses_count,
        pageSize=page_size,
        links=links
    )


@router.get("/abi")
def abi():
    tnt_abi = json.load(open("ebsi_sim/includes/abi_tnt.json", "r"))
    return tnt_abi
