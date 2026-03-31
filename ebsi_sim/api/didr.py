import json
import math
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi import Query
from starlette.status import HTTP_404_NOT_FOUND

from ebsi_sim.schemas import IdentifierListPublic, IdentifierPublic, IdentifierItemPublic, JsonRpcCreate, JsonRpcPublic, \
    PageLinksPublic
from ebsi_sim.services.didr import DidrService
from ebsi_sim.utils import get_current_user, User

router = APIRouter(prefix="/did-registry", tags=["did-registry"])


@router.post("/jsonrpc",
             description="The JSON-RPC API provides methods assisting the construction of blockchain transactions and interaction with the ledger, i.e. write operation on ledger.")
def rpc(current_user: Annotated[User, Depends(get_current_user)], payload: JsonRpcCreate,
        didr_service: DidrService = Depends()) -> JsonRpcPublic:
    json_rpc_result = didr_service.handle_rpc(current_user, payload)

    return JsonRpcPublic(
        jsonrpc="2.0",
        id=payload.id,
        result=json_rpc_result
    )


@router.get("/identifiers", description="Returns a list of identifiers.")
def read_identifiers(page_after: Annotated[int, Query(alias="page[after]")] = 1,
                     page_size: Annotated[int, Query(alias="page[size]")] = 10,
                     controller: str | None = None, didr_service: DidrService = Depends()) -> IdentifierListPublic:
    dids_count = didr_service.count_did_documents(controller=controller)
    n_pages = math.ceil(dids_count / page_size)

    links = PageLinksPublic(first=f"/identifiers?page[after]=1&page[size]={page_size}",
                            prev=f"/identifiers?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/identifiers?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/identifiers?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    dids = didr_service.list_did_documents(controller=controller, offset=(page_after - 1) * page_size, limit=page_size)
    items = []
    for d in dids:
        items.append(IdentifierItemPublic(did=d.did, href=f"/identifiers/{d.did}"))

    return IdentifierListPublic(
        self=f"/identifiers?page[after]={page_after}&page[size]={page_size}",
        items=items,
        total=dids_count,
        pageSize=page_size,
        links=links
    )


@router.get("/identifiers/{did}", description="Gets the identifier corresponding to the DID.")
def read_identifier(did: str, valid_at=None, didr_service: DidrService = Depends()) -> IdentifierPublic:
    identifier = didr_service.get_did_document(did)
    if not identifier:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Identifier not found")
    did_controllers = identifier.controllers
    vmethods = identifier.verification_methods
    vrelationships = identifier.verification_relationships

    return IdentifierPublic(
        did=identifier.did,
        controller=[did_controller.did for did_controller in did_controllers],
        context=identifier.context,
        verificationMethod=vmethods,
        authentication=[vrel.vmethodid for vrel in vrelationships if vrel.name == "authentication"],
        assertionMethod=[vrel.vmethodid for vrel in vrelationships if vrel.name == "assertionMethod"],
        keyAgreement=[vrel.vmethodid for vrel in vrelationships if vrel.name == "keyAgreement"],
        capabilityInvocation=[vrel.vmethodid for vrel in vrelationships if vrel.name == "capabilityInvocation"],
        capabilityDelegation=[vrel.vmethodid for vrel in vrelationships if vrel.name == "capabilityDelegation"]
    )


@router.get("/abi")
def abi():
    didr_abi = json.load(open("ebsi_sim/includes/abi_didr.json", "r"))
    return didr_abi
