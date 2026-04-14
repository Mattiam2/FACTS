import math
from typing import Annotated

from fastapi import Query, Path
from fastapi import Response, APIRouter, Depends, HTTPException
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from web3 import Web3

from ebsi_sim.core.auth import User, get_current_user
from ebsi_sim.core.exceptions import EBSINotFoundError
from ebsi_sim.schemas import AccessListPublic, DocumentItemPublic, DocumentListPublic, DocumentPublic, EventItemPublic, \
    EventListPublic, EventPublic, JsonRpcCreate, JsonRpcPublic, PageLinksPublic, TimestampPublic, VersionEnum
from ebsi_sim.services.didr import DidrService
from ebsi_sim.services.tnt import TntService

w3 = Web3()
router = APIRouter(prefix="/track-and-trace", tags=["track-and-trace"])


@router.post("/jsonrpc", summary="JSON-RPC API",
             description="The JSON-RPC API provides methods assisting the construction of blockchain transactions and interaction with the ledger, i.e. write operation on ledger.",
             responses={
                 200: {"description": "Response"},
                 400: {"description": "Bad request"}
             })
def rpc(current_user: Annotated[User, Depends(get_current_user)], payload: JsonRpcCreate,
        tnt_service: TntService = Depends()) -> JsonRpcPublic:
    """
    JSON-RPC API endpoint for simulating the handling of blockchain transactions and interaction with the ledger.
    """

    json_rpc_result = tnt_service.handle_rpc(current_user, payload)

    return JsonRpcPublic(
        jsonrpc="2.0",
        id=payload.id,
        result=json_rpc_result
    )


@router.head("/accesses", summary="Check access",
             description="Checks if the DID is included in the allowlist of TnT Document creators or not.",
             responses={
                 204: {"description": "Success"},
                 400: {"description": "Bad Request Error"},
                 404: {"description": "DID not found in the allowlist"},
                 500: {"description": "Internal Server Error"},
             })
def check_access(creator: Annotated[str, Query(description="DID to check")], didr_service: DidrService = Depends()):
    """
    Checks if the DID is included in the allowlist of TnT Document creators or not.
    """
    did_creator = didr_service.get_did_document(did=creator)

    if not did_creator or not did_creator.tnt_authorized:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="DID not found in the allowlist")

    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get("/accesses", summary="Get accesses", description="Get accesses filtered by subject.",
            responses={
                200: {"description": "Success"},
                400: {"description": "Bad Request"},
                404: {"description": "Not found"},
                500: {"description": "Internal Server Error"}
            })
def read_subject_accesses(subject: Annotated[str, Query(description="Subject DID")],
                          page_after: Annotated[int, Query(alias="page[after]",
                                                           description="Cursor that points to the end of the page of data that has been returned.")] = 1,
                          page_size: Annotated[int, Query(alias="page[size]",
                                                          description="Defines the maximum number of objects that may be returned.")] = 10,
                          tnt_service: TntService = Depends()) -> AccessListPublic:
    """
    Get accesses filtered by subject.
    """
    if page_size == 0:
        page_size = 10

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
        page_size=page_size,
        links=links
    )


@router.get("/documents", summary="List documents", description="Returns a list of documents.",
            responses={
                200: {"description": "Success"},
                400: {"description": "Bad Request Error"},
                500: {"description": "Internal Server Error"}
            })
def read_docs(page_after: Annotated[int, Query(alias="page[after]",
                                               description="Cursor that points to the end of the page of data that has been returned.")] = 1,
              page_size: Annotated[int, Query(alias="page[size]",
                                              description="Defines the maximum number of objects that may be returned.")] = 10,
              tnt_service: TntService = Depends()) -> DocumentListPublic:
    """
    Returns a list of documents.
    """
    if page_size == 0:
        page_size = 10

    docs_count = tnt_service.count_documents()
    n_pages = math.ceil(docs_count / page_size)

    links = PageLinksPublic(first=f"/documents?page[after]=1&page[size]={page_size}",
                            prev=f"/documents?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/documents?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/documents?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    docs = tnt_service.list_documents(offset=(page_after - 1) * page_size, limit=page_size)
    items = []
    for doc in docs:
        items.append(DocumentItemPublic(document_id=doc.id, href=f"/documents/{doc.id}"))

    return DocumentListPublic(
        self=f"/documents?page[after]={page_after}&page[size]={page_size}",
        items=items,
        total=docs_count,
        page_size=page_size,
        links=links
    )


@router.get("/documents/{document_id}", summary="Get a document",
            description="Gets the document corresponding to the ID.",
            responses={
                200: {"description": "Success"},
                400: {"description": "Bad Request"},
                404: {"description": "Not found"},
                500: {"description": "Internal Server Error"}
            })
def read_doc(document_id: Annotated[str, Path(description="The 32-bytes ID of the document, encoded in hexadecimal.")],
             version: Annotated[VersionEnum, Query(
                 description="Version of the endpoint to use. Defaults to the latest version.")] = VersionEnum.latest,
             tnt_service: TntService = Depends()) -> DocumentPublic:
    """
    Gets the document corresponding to the ID.
    """
    doc = tnt_service.get_document(document_id)
    if not doc:
        raise EBSINotFoundError("Document not found")

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


@router.get("/documents/{document_id}/events", summary="List events", description="Returns a list of events.",
            responses={
                200: {"description": "Success"},
                400: {"description": "Bad Request Error"},
                404: {"description": "Not found"},
                500: {"description": "Internal Server Error"}
            })
def read_doc_events(
        document_id: Annotated[str, Path(description="The 32-bytes ID of the document, encoded in hexadecimal.")],
        page_after: Annotated[int, Query(alias="page[after]",
                                         description="Cursor that points to the end of the page of data that has been returned.")] = 1,
        page_size: Annotated[int, Query(alias="page[size]",
                                        description="Defines the maximum number of objects that may be returned.")] = 10,
        tnt_service: TntService = Depends()) -> EventListPublic:
    """
    Returns a list of events.
    """
    if page_size == 0:
        page_size = 10

    document = tnt_service.get_document(document_id)
    if not document:
        raise EBSINotFoundError("Document not found")

    events_count = tnt_service.count_events(document_id=document_id)
    n_pages = math.ceil(events_count / page_size)

    links = PageLinksPublic(first=f"/documents/{document_id}/events?page[after]=1&page[size]={page_size}",
                            prev=f"/documents/{document_id}/events?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/documents/{document_id}/events?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/documents/{document_id}/events?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    events = tnt_service.list_events(offset=(page_after - 1) * page_size, limit=page_size, document_id=document_id)

    items = []
    for event in events:
        items.append(EventItemPublic(event_id=event.id, href=f"/documents/{document_id}/events/{event.id}"))

    return EventListPublic(
        self=f"/documents/{document_id}/events?page[after]={page_after}&page[size]={page_size}",
        items=items,
        total=events_count,
        page_size=page_size,
        links=links
    )


@router.get("/documents/{document_id}/events/{event_id}", summary="Get an event",
            description="Gets the event corresponding to the document ID and event ID.",
            responses={
                200: {"description": "Success"},
                400: {"description": "Bad Request Error"},
                404: {"description": "Not found"},
                500: {"description": "Internal Server Error"}
            })
def read_doc_event(
        document_id: Annotated[str, Path(description="The 32-bytes ID of the document, encoded in hexadecimal.")],
        event_id: Annotated[str, Path(description="The 32-bytes ID of the event, encoded in hexadecimal.")],
        tnt_service: TntService = Depends()) -> EventPublic:
    """
    Gets the event corresponding to the document ID and event ID.
    """
    events = tnt_service.list_events(document_id=document_id, id=event_id)
    if not events or len(events) == 0:
        raise EBSINotFoundError("Event not found")
    event = events[0]

    timestamp = TimestampPublic(
        datetime=event.timestamp_datetime.isoformat() if event.timestamp_datetime else None,
        source=event.timestamp_source,
        proof=event.timestamp_proof
    )

    event_public = EventPublic(**event.model_dump(), timestamp=timestamp)

    return event_public


@router.get("/documents/{document_id}/accesses", summary="List accesses",
            description="Returns a list of accesses related to the document.",
            responses={
                200: {"description": "Success"},
                400: {"description": "Bad Request Error"},
                404: {"description": "Not found"},
                500: {"description": "Internal Server Error"}
            })
def read_doc_accesses(
        document_id: Annotated[str, Path(description="The 32-bytes ID of the document, encoded in hexadecimal.")],
        page_after: Annotated[int, Query(alias="page[after]",
                                         description="Cursor that points to the end of the page of data that has been returned.")] = 1,
        page_size: Annotated[int, Query(alias="page[size]",
                                        description="Defines the maximum number of objects that may be returned.")] = 10,
        tnt_service: TntService = Depends()) -> AccessListPublic:
    """
    Returns a list of accesses related to the document.
    """
    if page_size == 0:
        page_size = 10

    document = tnt_service.get_document(document_id)
    if not document:
        raise EBSINotFoundError("Document not found")

    accesses_count = tnt_service.count_accesses(document_id=document_id)
    n_pages = math.ceil(accesses_count / page_size)

    links = PageLinksPublic(first=f"/documents/{document_id}/accesses?page[after]=1&page[size]={page_size}",
                            prev=f"/documents/{document_id}/accesses?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/documents/{document_id}/accesses?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/documents/{document_id}/accesses?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    accesses = tnt_service.list_accesses(document_id=document_id, offset=(page_after - 1) * page_size, limit=page_size)

    return AccessListPublic(
        self=f"/documents/{document_id}/accesses?page[after]={page_after}&page[size]={page_size}&documentId={document_id}",
        items=accesses,
        total=accesses_count,
        page_size=page_size,
        links=links
    )


@router.get("/abi", summary="Get ABI", description="Returns the ABI of Track and Trace SC v1.",
            responses={
                200: {"description": "Success"}
            })
def abi(tnt_service: TntService = Depends()):
    """
    Returns the ABI of Track and Trace SC v1.
    """
    tnt_abi = tnt_service.get_abi()
    return tnt_abi
