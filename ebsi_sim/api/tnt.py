import json
import math

import rlp
from eth_account import Account
from eth_account._utils.legacy_transactions import Transaction
from fastapi import Response, APIRouter, Depends, HTTPException
from typing import Annotated

from fastapi import Query
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, \
    HTTP_500_INTERNAL_SERVER_ERROR, HTTP_403_FORBIDDEN
from web3 import Web3
from web3.contract.base_contract import BaseContractFunction

from ebsi_sim.schemas import AccessListPublic, DocumentItemPublic, DocumentListPublic, DocumentPublic, EventItemPublic, \
    EventListPublic, EventPublic, JsonRpcCreate, JsonRpcPublic, PageLinksPublic, TimestampPublic, VersionEnum, \
    PermissionEnum
from ebsi_sim.services.tnt import TntService
from ebsi_sim.utils import User, get_current_user, check_scopes, booleanize

w3 = Web3()
router = APIRouter(prefix="/track-and-trace", tags=["track-and-trace"])

tnt_abi = json.load(open("ebsi_sim/includes/abi_tnt.json", "r"))

register_address = "0x823BBc0ceE3dE3B61AcfA0CEedb951AB9a013F05"

eth_contract = w3.eth.contract(
    abi=tnt_abi
)


@router.post("/jsonrpc",
             description="The JSON-RPC API provides methods assisting the construction of blockchain transactions and interaction with the ledger, i.e. write operation on ledger.")
def rpc(current_user: Annotated[User, Depends(get_current_user)], payload: JsonRpcCreate, tnt_service: TntService = Depends()) -> JsonRpcPublic:
    is_authorized = check_scopes(current_user, payload.method, {
        "authoriseDid": ["tnt_authorise"],
        "createDocument": ["tnt_create"],
        "removeDocument": ["tnt_write"],
        "grantAccess": ["tnt_write"],
        "revokeAccess": ["tnt_write"],
        "writeEvent": ["tnt_write"],
        "sendSignedTransaction": ["tnt_authorise", "tnt_create", "tnt_write"]
    })

    if not is_authorized:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden method")

    params = payload.params[0]
    if payload.method in ("authoriseDid", "createDocument", "removeDocument", "grantAccess", "revokeAccess",
                          "writeEvent"):

        abi_functions: list[BaseContractFunction] = eth_contract.find_functions_by_name(payload.method)

        params_set = set(params.keys())
        params_set.remove("from")

        if payload.method == "createDocument":
            if "didEbsiCreator" in params and current_user.sub != params['didEbsiCreator']:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="didEbsiCreator is not the same as the subject")

        if payload.method == "removeDocument":
            document = tnt_service.getDocument(params['eventParams'][0]['documentHash'])
            if document.creator != current_user.sub:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Document creator is not the same as the subject")


        if payload.method == "grantAccess":
            if "grantedByAccount" in params and current_user.sub != params['grantedByAccount']:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="grantedByAccount is not the same as the subject")
            user_accesses = tnt_service.listAccesses(subject=params['grantedByAccount'], document_id=params['documentHash'])
            document = tnt_service.getDocument(params['documentHash'])
            if document is None:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Document not found")
            if document.creator != params['grantedByAccount']:
                if params['permission'] != PermissionEnum.write:
                    raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="grantedByAccount is not the same as the creator")
                else:
                    is_delegated = bool([access for access in user_accesses if access.permission == PermissionEnum.delegate])
                    if not is_delegated:
                        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Permission not granted")

        if payload.method == 'revokeAccess':
            if "revokedByAccount" in params and current_user.sub != params['revokedByAccount']:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="revokedByAccount is not the same as the subject")
            document = tnt_service.getDocument(params['documentHash'])
            if document is None:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Document not found")
            if document.creator != params['revokedByAccount']:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="revokedByAccount is not the same as the creator")

        if payload.method == "writeEvent":
            document = tnt_service.getDocument(params['eventParams'][0]['documentHash'])
            user_accesses = tnt_service.listAccesses(subject=params['grantedByAccount'], document_id=params['documentHash'], permission=PermissionEnum.write)
            if document is None:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Document not found")
            if user_accesses is None:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Permission not granted")

        candidate_function: BaseContractFunction = next(
            (tmp_fn for tmp_fn in abi_functions if set(tmp_fn.argument_names) == params_set), None)

        if not candidate_function:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid arguments")

        abi_args = {k: booleanize(params[k]) for k in candidate_function.argument_names if k in params}
        unsigned_transaction = candidate_function(**abi_args).build_transaction({"from": params['from'],
                                                                                  "to": register_address,
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

        decoded_transaction = rlp.decode(trans_signed_transaction, Transaction)

        if decoded_transaction != trans_unsigned_transaction:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid transaction")

        signer = Account.recover_transaction(trans_signed_transaction)
        if signer.lower() != decoded_transaction['from'].lower():
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid transaction")

        data = decoded_transaction['data']

        func_obj, params = eth_contract.decode_function_input(data=data)

        try:
            function = getattr(tnt_service, func_obj.fn_name)

            func_result = function(**params)
            json_rpc_result = "0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331"
        except Exception as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
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
def check_access(creator: Annotated[str, Query()], tnt_service: TntService = Depends()):
    creator_access = tnt_service.listAccesses(subject=creator)

    if not creator_access:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="DID not found in the allowlist")

    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get("/accesses", description="Get accesses filtered by subject.")
def read_subject_accesses(subject: str, page_after: Annotated[int, Query(alias="page[after]")] = 1,
                          page_size: Annotated[int, Query(alias="page[size]")] = 10, tnt_service: TntService = Depends()) -> AccessListPublic:

    accesses_count = tnt_service.countAccesses(subject=subject)
    n_pages = math.ceil(accesses_count / page_size)

    links = PageLinksPublic(first=f"/accesses?page[after]=1&page[size]={page_size}&subject={subject}",
                            prev=f"/accesses?page[after]={max(1, page_after - 1)}&page[size]={page_size}&subject={subject}",
                            next=f"/accesses?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}&subject={subject}",
                            last=f"/accesses?page[after]={max(n_pages, 1)}&page[size]={page_size}&subject={subject}")

    accesses = tnt_service.listAccesses(offset=(page_after - 1) * page_size, limit=page_size, subject=subject)

    return AccessListPublic(
        self=f"/accesses?page[after]={page_after}&page[size]={page_size}&subject={subject}",
        items=accesses,
        total=accesses_count,
        pageSize=page_size,
        links=links
    )


@router.get("/documents", description="Returns a list of documents.")
def read_docs(page_after: Annotated[int, Query(alias="page[after]")] = 1,
              page_size: Annotated[int, Query(alias="page[size]")] = 10, tnt_service: TntService = Depends()) -> DocumentListPublic:

    docs_count = tnt_service.countDocuments()
    n_pages = math.ceil(docs_count / page_size)

    links = PageLinksPublic(first=f"/documents?page[after]=1&page[size]={page_size}",
                            prev=f"/documents?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/documents?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/documents?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    docs = tnt_service.listDocuments(offset=(page_after - 1) * page_size, limit=page_size)
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
def read_doc(documentId: str, version: VersionEnum = VersionEnum.latest, tnt_service: TntService = Depends()) -> DocumentPublic:
    doc = tnt_service.getDocument(documentId)

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
def read_doc_events(documentId: str, page_after: Annotated[int, Query(alias="page[after]")] = 1,
                    page_size: Annotated[int, Query(alias="page[size]")] = 10, tnt_service: TntService = Depends()) -> EventListPublic:

    events_count = tnt_service.countEvents(document_id=documentId)
    n_pages = math.ceil(events_count / page_size)

    links = PageLinksPublic(first=f"/documents/{documentId}/events?page[after]=1&page[size]={page_size}",
                            prev=f"/documents/{documentId}/events?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/documents/{documentId}/events?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/documents/{documentId}/events?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    events = tnt_service.listEvents(offset=(page_after - 1) * page_size, limit=page_size, document_id=documentId)

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
    events = tnt_service.listEvents(document_id=documentId, id=eventId)
    event = events[0] if events else None

    timestamp = TimestampPublic(
        datetime=event.timestamp_datetime.isoformat(),
        source=event.timestamp_source,
        proof=event.timestamp_proof
    )

    event_public = EventPublic(**event.dict(), timestamp=timestamp)

    return event_public


@router.get("/documents/{documentId}/accesses", description="Returns a list of accesses related to the document.")
def read_doc_accesses(documentId: str, page_after: Annotated[int, Query(alias="page[after]")] = 1,
                      page_size: Annotated[int, Query(alias="page[size]")] = 10, tnt_service: TntService = Depends()) -> AccessListPublic:

    accesses_count = tnt_service.countAccesses(document_id=documentId)
    n_pages = math.ceil(accesses_count / page_size)

    links = PageLinksPublic(first=f"/documents/{documentId}/accesses?page[after]=1&page[size]={page_size}",
                            prev=f"/documents/{documentId}/accesses?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/documents/{documentId}/accesses?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/documents/{documentId}/accesses?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    accesses = tnt_service.listAccesses(document_id=documentId, offset=(page_after - 1) * page_size, limit=page_size)

    return AccessListPublic(
        self=f"/documents/{documentId}/accesses?page[after]={page_after}&page[size]={page_size}&documentId={documentId}",
        items=accesses,
        total=accesses_count,
        pageSize=page_size,
        links=links
    )


@router.get("/abi")
def abi() -> dict:
    return tnt_abi
