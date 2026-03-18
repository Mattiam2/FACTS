import json
import math
from typing import Annotated

import rlp
from eth_account import Account
from eth_account._utils.legacy_transactions import Transaction
from fastapi import APIRouter, HTTPException, Depends
from fastapi import Query
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from web3 import Web3
from web3.contract.base_contract import BaseContractFunction

from ebsi_sim.schemas import IdentifierListPublic, IdentifierPublic, IdentifierItemPublic, JsonRpcCreate, JsonRpcPublic, \
    PageLinksPublic
from ebsi_sim.services.didr import DidrService
from ebsi_sim.utils import get_current_user, User, check_scopes

w3 = Web3()

router = APIRouter(prefix="/did-registry", tags=["did-registry"])

didr_abi = json.load(open("ebsi_sim/includes/abi_didr.json", "r"))

register_address = "0x823BBc0ceE3dE3B61AcfA0CEedb951AB9a013F05"

eth_contract = w3.eth.contract(
    abi=didr_abi
)


@router.post("/jsonrpc",
             description="The JSON-RPC API provides methods assisting the construction of blockchain transactions and interaction with the ledger, i.e. write operation on ledger.")
def rpc(current_user: Annotated[User, Depends(get_current_user)], payload: JsonRpcCreate,
        didr_service: DidrService = Depends()) -> JsonRpcPublic:
    is_authorized = check_scopes(current_user, payload.method, {
        "insertDidDocument": ["didr_invite", "didr_write"],
        "updateBaseDocument": ["didr_write"],
        "addService": ["didr_write"],
        "revokeService": ["didr_write"],
        "addController": ["didr_write"],
        "revokeController": ["didr_write"],
        "addVerificationMethod": ["didr_write"],
        "addVerificationRelationship": ["didr_write"],
        "revokeVerificationMethod": ["didr_write"],
        "expireVerificationMethod": ["didr_write"],
        "rollVerificationMethod": ["didr_write"],
        "sendSignedTransaction": ["didr_invite", "didr_write"]
    })

    if not is_authorized:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden method")

    json_rpc_result = None
    params = payload.params[0]
    if payload.method in ("insertDidDocument", "updateBaseDocument", "addService", "revokeService", "addController",
                          "revokeController", "addVerificationMethod", "addVerificationRelationship",
                          "revokeVerificationMethod", "expireVerificationMethod", "rollVerificationMethod"):
        abi_functions: list[BaseContractFunction] = eth_contract.find_functions_by_name(payload.method)

        subject_did = params.get("did")
        if subject_did is not None and subject_did != current_user.sub:
            if payload.method == "insertDidDocument":
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden DID")
            sub_identifier = didr_service.getDidDocument(subject_did)
            controllers = sub_identifier.controllers
            if current_user.sub not in [c.did for c in controllers]:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden DID")

        candidate_function: BaseContractFunction = next(
            (tmp_fn for tmp_fn in abi_functions if set(tmp_fn.argument_names) == set(params.keys())), None)

        if not candidate_function:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid arguments")

        abi_args = {k: params[k] for k in candidate_function.argument_names if k in params}
        unsigned_transaction = candidate_function.call(**abi_args).build_transaction({"from": params['from'],
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

        function = getattr(didr_service, func_obj.fn_name)

        func_result = function(**params)
        json_rpc_result = "0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331"

    return JsonRpcPublic(
        jsonrpc="2.0",
        id=payload.id,
        result=json_rpc_result
    )


@router.get("/identifiers", description="Returns a list of identifiers.")
def read_identifiers(page_after: Annotated[int, Query(alias="page[after]")] = 1,
                     page_size: Annotated[int, Query(alias="page[size]")] = 10,
                     controller: str | None = None, didr_service: DidrService = Depends()) -> IdentifierListPublic:
    dids_count = didr_service.countDidDocuments(controller=controller)
    n_pages = math.ceil(dids_count / page_size)

    links = PageLinksPublic(first=f"/identifiers?page[after]=1&page[size]={page_size}",
                            prev=f"/identifiers?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/identifiers?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/identifiers?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    dids = didr_service.listDidDocuments(controller=controller, offset=(page_after - 1) * page_size, limit=page_size)
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
    identifier = didr_service.getDidDocument(did)
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


@router.post("/identifiers/{did}/actions", description="Performs an action on the identifier corresponding to the DID.")
def post_action_identifier(did: str, payload: JsonRpcCreate, didr_service: DidrService = Depends()) -> JsonRpcPublic:
    vmethods = didr_service.listVerificationMethods(did_controller=did)

    return JsonRpcPublic(
        jsonrpc="2.0",
        id=payload.id,
        result=(len(vmethods) > 0))


@router.get("/abi")
def abi() -> dict:
    return didr_abi
