import json
import math
import os
from datetime import datetime

import web3
from fastapi import Response, APIRouter, Depends, HTTPException
from typing import Annotated

from fastapi import Query
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, \
    HTTP_500_INTERNAL_SERVER_ERROR
from web3 import Web3
from web3.contract.base_contract import BaseContractFunction

from ebsi_sim.core.db import db
from ebsi_sim.repositories.access import AccessRepository
from ebsi_sim.repositories.document import DocumentRepository
from ebsi_sim.repositories.event import EventRepository
from ebsi_sim.schemas.access import AccessListPublic
from ebsi_sim.schemas.document import DocumentItemPublic, DocumentListPublic, DocumentPublic
from ebsi_sim.schemas.event import EventItemPublic, EventListPublic, EventPublic
from ebsi_sim.schemas.jsonrpc import JsonRpcCreate, JsonRpcPublic
from ebsi_sim.schemas.shared import PageLinksPublic, TimestampPublic, VersionEnum
from ebsi_sim.services import tnt

w3 = Web3()
router = APIRouter(prefix="/track-and-trace", tags=["track-and-trace"])


tnt_abi = json.load(open("ebsi_sim/core/tnt_abi.json", "r"))

register_address = "0x823BBc0ceE3dE3B61AcfA0CEedb951AB9a013F05"

eth_contract = w3.eth.contract(
    abi=tnt_abi
)


@router.post("/jsonrpc",
             description="The JSON-RPC API provides methods assisting the construction of blockchain transactions and interaction with the ledger, i.e. write operation on ledger.")
async def rpc(payload: JsonRpcCreate) -> JsonRpcPublic:
    params = payload.params[0]
    if payload.method in ("authoriseDid", "createDocument", "removeDocument", "grantAccess", "revokeAccess", "writeEvent"):
        abi_functions: list[BaseContractFunction] = sorted(eth_contract.find_functions_by_name(payload.method), key=lambda x: len(x.argument_names), reverse=True)
        abi_fn: BaseContractFunction | None = None
        for tmp_fn in abi_functions:
            if set(tmp_fn.argument_names).issubset(params.keys()):
                abi_fn = tmp_fn
                break
        if abi_fn is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid arguments")

        abi_args = {k: params[k] for k in abi_fn.argument_names if k in params}
        # noinspection PyCallingNonCallable
        unsigned_transaction = abi_fn(
            **abi_args).build_transaction({"from": params['from'], "to": register_address,
                                           "nonce": 0xb1d3,
                                           "chainId": 1234,
                                           "gas": 0,
                                           "gasLimit": 1000000,
                                           "gasPrice": 0})
        json_rpc_result = unsigned_transaction
    elif payload.method == "sendSignedTransaction":
        trans_protocol = params['protocol']
        trans_unsigned_transaction = params['unsignedTransaction']
        trans_signed_transaction = params['signedRawTransaction']

        data = trans_unsigned_transaction['data']

        func_obj, params = eth_contract.decode_function_input(data=data)

        function = getattr(tnt, func_obj.fn_name)

        func_result = function(**params)
        json_rpc_result = "0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331"
    else:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid method")

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
async def check_access(creator: Annotated[str, Query()]):
    access_repo = AccessRepository()
    creator_access = access_repo.list(subject=creator)

    if not creator_access:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="DID not found in the allowlist")

    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get("/accesses", description="Get accesses filtered by subject.")
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


@router.get("/documents", description="Returns a list of documents.")
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


@router.get("/documents/{documentId}", description="Gets the document corresponding to the ID.")
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


@router.get("/documents/{documentId}/events", description="Returns a list of events.")
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


@router.get("/documents/{documentId}/events/{eventId}", description="Gets the event corresponding to the document ID and event ID.")
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


@router.get("/documents/{documentId}/accesses", description="Returns a list of accesses related to the document.")
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
