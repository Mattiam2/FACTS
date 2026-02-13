import math
from datetime import datetime

from web3 import Web3
from fastapi import APIRouter, HTTPException
from typing import Annotated

from fastapi import Query
from starlette.status import HTTP_400_BAD_REQUEST

from ebsi_sim.core.db import db
from ebsi_sim.repositories.identifier import IdentifierRepository, VerificationRelationshipRepository, \
    VerificationMethodRepository, IdentifierControllerRepository
from ebsi_sim.schemas.identifier import IdentifierListPublic, IdentifierPublic, IdentifierItemPublic
from ebsi_sim.schemas.jsonrpc import JsonRpcCreate, JsonRpcPublic
from ebsi_sim.schemas.shared import PageLinksPublic

from ebsi_sim.services import didr

w3 = Web3()
router = APIRouter(prefix="/did-registry", tags=["did-registry"])

register_address = "0x823BBc0ceE3dE3B61AcfA0CEedb951AB9a013F05"

ABI = [
    {"inputs": [{"internalType": "address", "name": "_tprAddress", "type": "address"}], "stateMutability": "nonpayable",
     "type": "constructor"}, {"anonymous": False,
                              "inputs": [{"indexed": False, "internalType": "string", "name": "did", "type": "string"},
                                         {"indexed": False, "internalType": "string", "name": "baseDocument",
                                          "type": "string"}], "name": "BaseDocumentUpdated", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": False, "internalType": "string", "name": "did", "type": "string"},
                                    {"indexed": False, "internalType": "string", "name": "controller",
                                     "type": "string"}], "name": "ControllerAdded", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": False, "internalType": "string", "name": "did", "type": "string"},
                                    {"indexed": False, "internalType": "string", "name": "controller",
                                     "type": "string"}], "name": "ControllerRevoked", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": False, "internalType": "string", "name": "did", "type": "string"},
                                    {"indexed": False, "internalType": "string", "name": "baseDocument",
                                     "type": "string"},
                                    {"indexed": False, "internalType": "string", "name": "vMethodId", "type": "string"},
                                    {"indexed": False, "internalType": "bytes", "name": "publicKey", "type": "bytes"},
                                    {"indexed": False, "internalType": "bool", "name": "isSecp256k1", "type": "bool"},
                                    {"indexed": False, "internalType": "uint256", "name": "notBefore",
                                     "type": "uint256"},
                                    {"indexed": False, "internalType": "uint256", "name": "notAfter",
                                     "type": "uint256"}], "name": "DidDocumentInserted", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": False, "internalType": "uint8", "name": "version", "type": "uint8"}],
     "name": "Initialized", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": False, "internalType": "uint256", "name": "", "type": "uint256"}],
     "name": "NewVersion", "type": "event"}, {"anonymous": False, "inputs": [
        {"indexed": False, "internalType": "string", "name": "did", "type": "string"},
        {"indexed": False, "internalType": "string", "name": "vMethodId", "type": "string"},
        {"indexed": False, "internalType": "bytes", "name": "publicKey", "type": "bytes"},
        {"indexed": False, "internalType": "bool", "name": "isSecp256k1", "type": "bool"}],
                                              "name": "VerificationMethodAdded", "type": "event"}, {"anonymous": False,
                                                                                                    "inputs": [{
                                                                                                                   "indexed": False,
                                                                                                                   "internalType": "string",
                                                                                                                   "name": "did",
                                                                                                                   "type": "string"},
                                                                                                               {
                                                                                                                   "indexed": False,
                                                                                                                   "internalType": "string",
                                                                                                                   "name": "vMethodId",
                                                                                                                   "type": "string"},
                                                                                                               {
                                                                                                                   "indexed": False,
                                                                                                                   "internalType": "uint256",
                                                                                                                   "name": "notAfter",
                                                                                                                   "type": "uint256"}],
                                                                                                    "name": "VerificationMethodExpired",
                                                                                                    "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": False, "internalType": "string", "name": "did", "type": "string"},
                                    {"indexed": False, "internalType": "string", "name": "vMethodId", "type": "string"},
                                    {"indexed": False, "internalType": "uint256", "name": "notAfter",
                                     "type": "uint256"}], "name": "VerificationMethodRevoked", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": False, "internalType": "string", "name": "did", "type": "string"},
                                    {"indexed": False, "internalType": "string", "name": "vMethodId", "type": "string"},
                                    {"indexed": False, "internalType": "bytes", "name": "publicKey", "type": "bytes"},
                                    {"indexed": False, "internalType": "bool", "name": "isSecp256k1", "type": "bool"},
                                    {"indexed": False, "internalType": "uint256", "name": "notBefore",
                                     "type": "uint256"},
                                    {"indexed": False, "internalType": "uint256", "name": "notAfter",
                                     "type": "uint256"},
                                    {"indexed": False, "internalType": "string", "name": "oldVMethodId",
                                     "type": "string"},
                                    {"indexed": False, "internalType": "uint256", "name": "duration",
                                     "type": "uint256"}], "name": "VerificationMethodRolled", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": False, "internalType": "string", "name": "did", "type": "string"},
                                    {"indexed": False, "internalType": "string", "name": "name", "type": "string"},
                                    {"indexed": False, "internalType": "string", "name": "vMethodId", "type": "string"},
                                    {"indexed": False, "internalType": "uint256", "name": "notBefore",
                                     "type": "uint256"},
                                    {"indexed": False, "internalType": "uint256", "name": "notAfter",
                                     "type": "uint256"}], "name": "VerificationRelationshipAdded", "type": "event"},
    {"inputs": [], "name": "CONTROLLERS_DIAMOND_STORAGE_POSITION",
     "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "stateMutability": "view",
     "type": "function"}, {"inputs": [], "name": "DID_DOCUMENT_DIAMOND_STORAGE_POSITION",
                           "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
                           "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "TSC_DIAMOND_STORAGE_POSITION",
     "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "stateMutability": "view",
     "type": "function"}, {"inputs": [], "name": "VRELATIONSHIPS_DIAMOND_STORAGE_POSITION",
                           "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
                           "stateMutability": "view", "type": "function"}, {
        "inputs": [{"internalType": "string", "name": "did", "type": "string"},
                   {"internalType": "string", "name": "controller", "type": "string"}], "name": "addController",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable",
        "type": "function"}, {"inputs": [{"internalType": "string", "name": "did", "type": "string"},
                                         {"internalType": "string", "name": "vMethodId", "type": "string"},
                                         {"internalType": "bytes", "name": "publicKey", "type": "bytes"},
                                         {"internalType": "bool", "name": "isSecp256k1", "type": "bool"}],
                              "name": "addVerificationMethod",
                              "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                              "stateMutability": "nonpayable", "type": "function"}, {
        "inputs": [{"internalType": "string", "name": "did", "type": "string"},
                   {"internalType": "string", "name": "name", "type": "string"},
                   {"internalType": "string", "name": "vMethodId", "type": "string"},
                   {"internalType": "uint256", "name": "notBefore", "type": "uint256"},
                   {"internalType": "uint256", "name": "notAfter", "type": "uint256"}],
        "name": "addVerificationRelationship", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable", "type": "function"}, {
        "inputs": [{"internalType": "bytes", "name": "did", "type": "bytes"},
                   {"internalType": "address", "name": "controller", "type": "address"}], "name": "checkController",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "view",
        "type": "function"}, {"inputs": [{"internalType": "string", "name": "did", "type": "string"},
                                         {"internalType": "address", "name": "controller", "type": "address"}],
                              "name": "checkController",
                              "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                              "stateMutability": "view", "type": "function"}, {
        "inputs": [{"internalType": "string", "name": "did", "type": "string"},
                   {"internalType": "string", "name": "vMethodId", "type": "string"},
                   {"internalType": "uint256", "name": "notAfter", "type": "uint256"}],
        "name": "expireVerificationMethod", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "did", "type": "string"}], "name": "getDidDocument",
     "outputs": [{"internalType": "string", "name": "baseDocument", "type": "string"},
                 {"internalType": "string[]", "name": "controllers", "type": "string[]"},
                 {"internalType": "string[]", "name": "vMethodIds", "type": "string[]"}, {
                     "components": [{"internalType": "bytes", "name": "publicKey", "type": "bytes"},
                                    {"internalType": "bool", "name": "isSecp256k1", "type": "bool"},
                                    {"internalType": "bool", "name": "revoked", "type": "bool"}],
                     "internalType": "struct DidDocumentStorage.VMethod[]", "name": "vMethods", "type": "tuple[]"}, {
                     "components": [{"internalType": "string", "name": "name", "type": "string"},
                                    {"internalType": "string", "name": "vMethodId", "type": "string"},
                                    {"internalType": "uint256", "name": "notBefore", "type": "uint256"},
                                    {"internalType": "uint256", "name": "notAfter", "type": "uint256"},
                                    {"internalType": "uint256", "name": "indexDid", "type": "uint256"}],
                     "internalType": "struct DidDocumentStorage.VRelationship[]", "name": "vRelationships",
                     "type": "tuple[]"}], "stateMutability": "view", "type": "function"}, {
        "inputs": [{"internalType": "string", "name": "did", "type": "string"},
                   {"internalType": "uint256", "name": "timestamp", "type": "uint256"}],
        "name": "getDidDocumentByTimestamp",
        "outputs": [{"internalType": "string", "name": "baseDocument", "type": "string"},
                    {"internalType": "string[]", "name": "controllers", "type": "string[]"},
                    {"internalType": "string[]", "name": "vMethodIds", "type": "string[]"}, {
                        "components": [{"internalType": "bytes", "name": "publicKey", "type": "bytes"},
                                       {"internalType": "bool", "name": "isSecp256k1", "type": "bool"},
                                       {"internalType": "bool", "name": "revoked", "type": "bool"}],
                        "internalType": "struct DidDocumentStorage.VMethod[]", "name": "vMethods", "type": "tuple[]"}, {
                        "components": [{"internalType": "string", "name": "name", "type": "string"},
                                       {"internalType": "string", "name": "vMethodId", "type": "string"},
                                       {"internalType": "uint256", "name": "notBefore", "type": "uint256"},
                                       {"internalType": "uint256", "name": "notAfter", "type": "uint256"},
                                       {"internalType": "uint256", "name": "indexDid", "type": "uint256"}],
                        "internalType": "struct DidDocumentStorage.VRelationship[]", "name": "vRelationships",
                        "type": "tuple[]"}], "stateMutability": "view", "type": "function"}, {
        "inputs": [{"internalType": "uint256", "name": "page", "type": "uint256"},
                   {"internalType": "uint256", "name": "pageSize", "type": "uint256"}], "name": "getDids",
        "outputs": [{"internalType": "string[]", "name": "items", "type": "string[]"},
                    {"internalType": "uint256", "name": "total", "type": "uint256"},
                    {"internalType": "uint256", "name": "howMany", "type": "uint256"},
                    {"internalType": "uint256", "name": "prev", "type": "uint256"},
                    {"internalType": "uint256", "name": "next", "type": "uint256"}], "stateMutability": "view",
        "type": "function"}, {"inputs": [{"internalType": "string", "name": "controller", "type": "string"},
                                         {"internalType": "uint256", "name": "page", "type": "uint256"},
                                         {"internalType": "uint256", "name": "pageSize", "type": "uint256"}],
                              "name": "getDidsByController",
                              "outputs": [{"internalType": "string[]", "name": "items", "type": "string[]"},
                                          {"internalType": "uint256", "name": "total", "type": "uint256"},
                                          {"internalType": "uint256", "name": "howMany", "type": "uint256"},
                                          {"internalType": "uint256", "name": "prev", "type": "uint256"},
                                          {"internalType": "uint256", "name": "next", "type": "uint256"}],
                              "stateMutability": "view", "type": "function"}, {
        "inputs": [{"internalType": "string", "name": "vMethodId", "type": "string"},
                   {"internalType": "string", "name": "name", "type": "string"},
                   {"internalType": "uint256", "name": "page", "type": "uint256"},
                   {"internalType": "uint256", "name": "pageSize", "type": "uint256"}],
        "name": "getDidsByVerificationRelationship", "outputs": [{"components": [
            {"internalType": "string", "name": "did", "type": "string"},
            {"internalType": "uint256", "name": "notBefore", "type": "uint256"},
            {"internalType": "uint256", "name": "notAfter", "type": "uint256"}],
                                                                  "internalType": "struct VRelationshipsStorage.DidWithPeriod[]",
                                                                  "name": "items", "type": "tuple[]"},
                                                                 {"internalType": "uint256", "name": "total",
                                                                  "type": "uint256"},
                                                                 {"internalType": "uint256", "name": "howMany",
                                                                  "type": "uint256"},
                                                                 {"internalType": "uint256", "name": "prev",
                                                                  "type": "uint256"},
                                                                 {"internalType": "uint256", "name": "next",
                                                                  "type": "uint256"}], "stateMutability": "view",
        "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "v", "type": "uint256"}], "name": "initialize", "outputs": [],
     "stateMutability": "nonpayable", "type": "function"}, {
        "inputs": [{"internalType": "string", "name": "did", "type": "string"},
                   {"internalType": "string", "name": "baseDocument", "type": "string"},
                   {"internalType": "string", "name": "vMethodId", "type": "string"},
                   {"internalType": "bytes", "name": "publicKey", "type": "bytes"},
                   {"internalType": "bool", "name": "isSecp256k1", "type": "bool"},
                   {"internalType": "uint256", "name": "notBefore", "type": "uint256"},
                   {"internalType": "uint256", "name": "notAfter", "type": "uint256"}], "name": "insertDidDocument",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable",
        "type": "function"}, {"inputs": [], "name": "policyRegistryContract",
                              "outputs": [{"internalType": "contract IPolicyRegistry", "name": "", "type": "address"}],
                              "stateMutability": "view", "type": "function"}, {
        "inputs": [{"internalType": "string", "name": "did", "type": "string"},
                   {"internalType": "string", "name": "controller", "type": "string"}], "name": "revokeController",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable",
        "type": "function"}, {"inputs": [{"internalType": "string", "name": "did", "type": "string"},
                                         {"internalType": "string", "name": "vMethodId", "type": "string"},
                                         {"internalType": "uint256", "name": "notAfter", "type": "uint256"}],
                              "name": "revokeVerificationMethod",
                              "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                              "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"components": [
        {"internalType": "string", "name": "did", "type": "string"},
        {"internalType": "string", "name": "vMethodId", "type": "string"},
        {"internalType": "bytes", "name": "publicKey", "type": "bytes"},
        {"internalType": "bool", "name": "isSecp256k1", "type": "bool"},
        {"internalType": "uint256", "name": "notBefore", "type": "uint256"},
        {"internalType": "uint256", "name": "notAfter", "type": "uint256"},
        {"internalType": "string", "name": "oldVMethodId", "type": "string"},
        {"internalType": "uint256", "name": "duration", "type": "uint256"}],
                                                                                                 "internalType": "struct DidDocumentStorage.RollArgs",
                                                                                                 "name": "args",
                                                                                                 "type": "tuple"}],
                                                                                     "name": "rollVerificationMethod",
                                                                                     "outputs": [
                                                                                         {"internalType": "bool",
                                                                                          "name": "", "type": "bool"}],
                                                                                     "stateMutability": "nonpayable",
                                                                                     "type": "function"}, {
        "inputs": [{"internalType": "string", "name": "did", "type": "string"},
                   {"internalType": "string", "name": "baseDocument", "type": "string"}], "name": "updateBaseDocument",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable",
        "type": "function"},
    {"inputs": [], "name": "version", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"}]

eth_contract = w3.eth.contract(
    abi=ABI
)


@router.post("/jsonrpc",
             description="The JSON-RPC API provides methods assisting the construction of blockchain transactions and interaction with the ledger, i.e. write operation on ledger.")
async def rpc(payload: JsonRpcCreate) -> JsonRpcPublic:
    match payload.method:
        case "insertDidDocument":
            doc = payload.params[0]
            doc_from = doc['from']
            doc_did = doc['did']
            doc_base_document = doc['baseDocument']
            doc_vmethod_id = doc['vMethodId']
            doc_pkey = doc['publicKey']
            doc_is_secp256k1 = doc['isSecp256k1']
            doc_not_before = doc['notBefore']
            doc_not_after = doc['notAfter']

            unsigned_transaction = eth_contract.functions.insertDidDocument(
                did=doc_did, baseDocument=doc_base_document, vMethodId=doc_vmethod_id, publicKey=doc_pkey,
                isSecp256k1=doc_is_secp256k1, notBefore=doc_not_before, notAfter=doc_not_after
            ).build_transaction({"from": doc_from, "to": register_address,
                    "nonce": 0xb1d3,
                    "chainId": 1234,
                    "gas": 0,
                    "gasLimit": 1000000,
                    "gasPrice": 0})

            return JsonRpcPublic(
                jsonrpc="2.0",
                id=payload.id,
                result=unsigned_transaction
            )
        case "updateBaseDocument":
            doc_params = payload.params
            for doc in doc_params:
                doc_from = doc['from']
                doc_did = doc['did']
                doc_base_document = doc['baseDocument']

                did_repo = IdentifierRepository()
                did_repo.update(commit=False, id=doc_did, context=doc_base_document)
            db.session.commit()
        case "addService":
            pass
        case "revokeService":
            pass
        case "addController":
            doc_params = payload.params
            for doc in doc_params:
                doc_from = doc['from']
                doc_did = doc['did']
                doc_controller = doc['controller']

                did_controller_repo = IdentifierControllerRepository()
                did_controller_repo.create(commit=False, identifier_did=doc_did, did_controller=doc_controller)
            db.session.commit()
        case "revokeController":
            doc_params = payload.params
            for doc in doc_params:
                doc_from = doc['from']
                doc_did = doc['did']
                doc_controller = doc['controller']

                did_controller_repo = IdentifierControllerRepository()
                controllers = did_controller_repo.list(identifier_did=doc_did, did_controller=doc_controller)
                if len(controllers) == 1:
                    did_controller_repo.delete(commit=False, id=controllers[0].id)
            db.session.commit()
        case "addVerificationMethod":
            doc_params = payload.params
            for doc in doc_params:
                doc_from = doc['from']
                doc_did = doc['did']
                doc_vmethod_id = doc['vMethodId']
                doc_pkey = doc['publicKey']
                doc_is_secp256k1 = doc['isSecp256k1']

                full_vmethod_id = f"{doc_did}#{doc_vmethod_id}"
                vmethod_repo = VerificationMethodRepository()
                vmethod_repo.create(commit=False, id=full_vmethod_id, did_controller=doc_did, type="JsonWebKey2020",
                                    public_key=doc_pkey, issecp256k1=doc_is_secp256k1)
            db.session.commit()
        case "addVerificationRelationship":
            doc_params = payload.params
            for doc in doc_params:
                doc_from = doc['from']
                doc_did = doc['did']
                doc_name = doc['name']
                doc_vmethod_id = doc['vMethodId']
                doc_not_before = datetime.fromtimestamp(doc['notBefore'])
                doc_not_after = datetime.fromtimestamp(doc['notAfter'])

                full_vmethod_id = f"{doc_did}#{doc_vmethod_id}"
                vrelationship_repo = VerificationRelationshipRepository()
                vrelationship_repo.create(commit=False, identifier_did=doc_did, name=doc_name,
                                          vmethodid=full_vmethod_id,
                                          notbefore=doc_not_before, notafter=doc_not_after)
            db.session.commit()
        case "revokeVerificationMethod" | "expireVerificationMethod":
            doc_params = payload.params
            for doc in doc_params:
                doc_from = doc['from']
                doc_did = doc['did']
                doc_vmethod_id = doc['vMethodId']
                doc_not_after = datetime.fromtimestamp(doc['notAfter'])

                full_vmethod_id = f"{doc_did}#{doc_vmethod_id}"
                vmethod_repo = VerificationMethodRepository()
                vmethod = vmethod_repo.get(id=full_vmethod_id)
                vmethod_repo.update(commit=False, id=vmethod.id, notafter=doc_not_after)
            db.session.commit()
        case "rollVerificationMethod":
            pass
        case "sendSignedTransaction":
            trans = payload.params[0]
            trans_protocol = trans['protocol']
            trans_unsigned_transaction = trans['unsignedTransaction']
            trans_signed_transaction = trans['signedRawTransaction']

            data = trans_unsigned_transaction['data']

            func_obj, params = eth_contract.decode_function_input(data=data)
            func_name = func_obj.fn_name

            func = getattr(didr, func_name)

            func_result = func(**params)
        case _:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid method")

    return JsonRpcPublic(
        jsonrpc="2.0",
        id=payload.id,
        result={"status": "success", "message": "Operation completed successfully"}
    )


@router.get("/identifiers", description="Returns a list of documents.")
async def read_identifiers(page_after: Annotated[int, Query(alias="page[after]")] = 1,
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
async def read_identifier(did: str, valid_at=None) -> IdentifierPublic:
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
async def post_action_identifier(did: str, payload: JsonRpcCreate) -> JsonRpcPublic:
    vmethod_repo = VerificationMethodRepository()
    vmethods = vmethod_repo.list(did_controller=did)

    return JsonRpcPublic(
        jsonrpc="2.0",
        id=payload.id,
        result=(vmethods.count() > 0))


@router.get("/abi")
async def abi():
    pass
