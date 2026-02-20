import json
import math
from datetime import datetime

from web3 import Web3
from fastapi import APIRouter, HTTPException
from typing import Annotated

from fastapi import Query
from starlette.status import HTTP_400_BAD_REQUEST
from web3.contract.base_contract import BaseContractFunction

from ebsi_sim.core.db import db
from ebsi_sim.repositories.identifier import IdentifierRepository, VerificationRelationshipRepository, \
    VerificationMethodRepository, IdentifierControllerRepository
from ebsi_sim.schemas.identifier import IdentifierListPublic, IdentifierPublic, IdentifierItemPublic
from ebsi_sim.schemas.jsonrpc import JsonRpcCreate, JsonRpcPublic
from ebsi_sim.schemas.shared import PageLinksPublic

from ebsi_sim.services import didr

w3 = Web3()

router = APIRouter(prefix="/did-registry", tags=["did-registry"])

didr_abi = json.load(open("ebsi_sim/files/abi_didr.json", "r"))

register_address = "0x823BBc0ceE3dE3B61AcfA0CEedb951AB9a013F05"

eth_contract = w3.eth.contract(
    abi=didr_abi
)


@router.post("/jsonrpc",
             description="The JSON-RPC API provides methods assisting the construction of blockchain transactions and interaction with the ledger, i.e. write operation on ledger.")
def rpc(payload: JsonRpcCreate) -> JsonRpcPublic:
    params = payload.params[0]
    if payload.method in ("insertDidDocument", "updateBaseDocument", "addService", "revokeService", "addController",
                          "revokeController", "addVerificationMethod", "addVerificationRelationship",
                          "revokeVerificationMethod", "expireVerificationMethod", "rollVerificationMethod"):
        abi_functions: list[BaseContractFunction] = sorted(eth_contract.find_functions_by_name(payload.method),
                                                           key=lambda x: len(x.argument_names), reverse=True)
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

        function = getattr(didr, func_obj.fn_name)

        func_result = function(**params)
        json_rpc_result = "0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331"
    else:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid method")

    return JsonRpcPublic(
        jsonrpc="2.0",
        id=payload.id,
        result=json_rpc_result
    )


@router.get("/identifiers", description="Returns a list of documents.")
def read_identifiers(page_after: Annotated[int, Query(alias="page[after]")] = 1,
                           page_size: Annotated[int, Query(alias="page[size]")] = 10,
                           controller: str | None = None) -> IdentifierListPublic:
    did_repo = IdentifierControllerRepository()
    dids_count = did_repo.count(did_controller=controller)
    n_pages = math.ceil(dids_count / page_size)

    links = PageLinksPublic(first=f"/identifiers?page[after]=1&page[size]={page_size}",
                            prev=f"/identifiers?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/identifiers?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/identifiers?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    dids = did_repo.list(did_controller=controller, offset=(page_after - 1) * page_size, limit=page_size)
    items = []
    for d in dids:
        items.append(IdentifierItemPublic(did=d.identifier_did, href=f"/identifiers/{d.identifier_did}"))

    return IdentifierListPublic(
        self=f"/identifiers?page[after]={page_after}&page[size]={page_size}",
        items=items,
        total=dids_count,
        pageSize=page_size,
        links=links
    )


@router.get("/identifiers/{did}", description="Gets the document corresponding to the ID.")
def read_identifier(did: str, valid_at=None) -> IdentifierPublic:
    did_repo = IdentifierRepository()
    did_controller_repo = IdentifierControllerRepository()
    vmethod_repo = VerificationMethodRepository()
    vrelationship_repo = VerificationRelationshipRepository()

    identifier = did_repo.get(did)
    did_controllers = did_controller_repo.list(identifier_did=did)
    vmethods = vmethod_repo.list(did_controller=did)
    vrelationships = vrelationship_repo.list(identifier_did=did)

    return IdentifierPublic(
        did=identifier.did,
        controller=[did_controller.did_controller for did_controller in did_controllers],
        context=identifier.context,
        verificationMethod=vmethods,
        authentication=[vrel.vmethodid for vrel in vrelationships if vrel.name == "authentication"],
        assertionMethod=[vrel.vmethodid for vrel in vrelationships if vrel.name == "assertionMethod"],
        keyAgreement=[vrel.vmethodid for vrel in vrelationships if vrel.name == "keyAgreement"],
        capabilityInvocation=[vrel.vmethodid for vrel in vrelationships if vrel.name == "capabilityInvocation"],
        capabilityDelegation=[vrel.vmethodid for vrel in vrelationships if vrel.name == "capabilityDelegation"]
    )


@router.post("/identifiers/{did}/actions", description="Returns a list of events.")
def post_action_identifier(did: str, payload: JsonRpcCreate) -> JsonRpcPublic:
    vmethod_repo = VerificationMethodRepository()
    vmethods = vmethod_repo.list(did_controller=did)

    return JsonRpcPublic(
        jsonrpc="2.0",
        id=payload.id,
        result=(vmethods.count() > 0))


@router.get("/abi")
def abi() -> dict:
    return didr_abi
