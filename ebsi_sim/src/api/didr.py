import math
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi import Query
from fastapi.params import Path
from starlette.status import HTTP_404_NOT_FOUND

from ebsi_sim.src.core.auth import get_current_user, User
from ebsi_sim.src.schemas import IdentifierListPublic, IdentifierPublic, IdentifierItemPublic, JsonRpcCreate, JsonRpcPublic, \
    PageLinksPublic
from ebsi_sim.src.services.didr import DidrService

router = APIRouter(prefix="/did-registry", tags=["did-registry"])


@router.post("/jsonrpc", summary="JSON-RPC API",
             description="The JSON-RPC API provides methods assisting the construction of blockchain transactions and interaction with the ledger, i.e. write operation on ledger.",
             responses={
                 200: {"description": "Response"},
                 400: {"description": "Bad request"}
             })
def rpc(current_user: Annotated[User, Depends(get_current_user)], payload: JsonRpcCreate,
        didr_service: DidrService = Depends()) -> JsonRpcPublic:
    """
    The JSON-RPC API provides methods assisting the construction of blockchain transactions and interaction with the ledger, i.e. write operation on ledger.
    """
    json_rpc_result = didr_service.handle_rpc(current_user, payload)

    return JsonRpcPublic(
        jsonrpc="2.0",
        id=payload.id,
        result=json_rpc_result
    )


@router.get("/identifiers", summary="List identifiers", description="Returns a list of identifiers.",
            responses={
                200: {"description": "Success"},
                400: {"description": "Bad Request Error"},
                500: {"description": "Internal Server Error"}
            })
def read_identifiers(page_after: Annotated[int, Query(alias="page[after]",
                                                      description="Cursor that points to the end of the page of data that has been returned.")] = 1,
                     page_size: Annotated[int, Query(alias="page[size]",
                                                     description="Defines the maximum number of objects that may be returned.")] = 10,
                     controller: Annotated[str | None, Query(description="Filter by controller DID.")] = None,
                     didr_service: DidrService = Depends()) -> IdentifierListPublic:
    """
    Returns a list of identifiers.
    """
    if page_size == 0:
        page_size = 10

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
        page_size=page_size,
        links=links
    )


@router.get("/identifiers/{did}", summary="Get a DID document",
            description="Returns the DID document corresponding to the DID.",
            responses={
                200: {"description": "Success. A user wallet gets DID resolution."},
                400: {"description": "Bad Request"},
                404: {"description": "Not found"},
                500: {"description": "Internal Server Error"}
            })
def read_identifier(did: Annotated[str, Path(description="A DID to be resolved.")],
                    valid_at: Annotated[str, Query(
                        alias="valid-at",
                        description="This option is used to get a the version in the past of a DID document. It must be a date in ISO-8601 format")] = None,
                    didr_service: DidrService = Depends()) -> IdentifierPublic:
    """
    Returns the DID document corresponding to the DID.
    """
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


@router.get("/abi", summary="Get ABI", description="Returns the ABI of DID Registry SC v3.",
            responses={
                200: {"description": "Success"}
            })
def abi(didr_service: DidrService = Depends()):
    """
    Returns the ABI of DID Registry SC v3.
    """
    didr_abi = didr_service.get_abi()
    return didr_abi
