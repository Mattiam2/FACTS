import math
from datetime import datetime

from fastapi import Response, APIRouter, Depends, HTTPException
from typing import Annotated, Optional

from fastapi import Query
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, \
    HTTP_500_INTERNAL_SERVER_ERROR

from ebsi_sim.core.db import db
from ebsi_sim.repositories.access import AccessRepository
from ebsi_sim.repositories.document import DocumentRepository
from ebsi_sim.repositories.event import EventRepository
from ebsi_sim.repositories.identifier import IdentifierRepository, VerificationRelationshipRepository, \
    VerificationMethodRepository, IdentifierControllerRepository
from ebsi_sim.schemas.access import AccessListPublic
from ebsi_sim.schemas.document import DocumentItemPublic, DocumentListPublic, DocumentPublic
from ebsi_sim.schemas.event import EventItemPublic, EventListPublic, EventPublic
from ebsi_sim.schemas.identifier import IdentifierListPublic, IdentifierPublic
from ebsi_sim.schemas.jsonrpc import JsonRpcCreate, JsonRpcPublic
from ebsi_sim.schemas.shared import PageLinksPublic, TimestampPublic, VersionEnum

router = APIRouter(prefix="/did-registry", tags=["did-registry"])


@router.post("/jsonrpc",
             description="The JSON-RPC API provides methods assisting the construction of blockchain transactions and interaction with the ledger, i.e. write operation on ledger.")
async def rpc(payload: JsonRpcCreate) -> JsonRpcPublic:
    match payload.method:
        case "insertDidDocument":
            doc_params = payload.params
            for doc in doc_params:
                doc_from = doc['from']
                doc_did = doc['did']
                doc_base_document = doc['baseDocument']
                doc_vmethod = doc['vMethodId']
                doc_pkey = doc['publicKey']
                doc_is_secp256k1 = doc['isSecp256k1']
                doc_not_before = doc['notBefore']
                doc_not_after = doc['notAfter']

                did_repo = IdentifierRepository()
                did_repo.create(commit=False, id=doc_did, context=doc_base_document)

                full_vmethod_id = f"{doc_did}#{doc_vmethod}"

                vmethod_repo = VerificationMethodRepository()
                vmethod_repo.create(commit=False, id=full_vmethod_id, did_controller=doc_did, type="JsonWebKey2020",
                                    public_key=doc_pkey, issecp256k1=doc_is_secp256k1)

                vrelationship_repo = VerificationRelationshipRepository()
                vrelationship_repo.create(commit=False, identifier_did=doc_did, name="capabilityInvocation",
                                          vmethodid=full_vmethod_id, notbefore=doc_not_before, notafter=doc_not_after)
            db.session.commit()
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
            service_params = payload.params
            for service in service_params:
                service_from = service['from']
                service_did = service['did']
                service_content = service['type']
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
                doc_not_before = doc['notBefore']
                doc_not_after = doc['notAfter']

                full_vmethod_id = f"{doc_did}#{doc_vmethod_id}"
                vrelationship_repo = VerificationRelationshipRepository()
                vrelationship_repo.create(commit=False, identifier_did=doc_did, name=doc_name, vmethodid=full_vmethod_id,
                                          notbefore=doc_not_before, notafter=doc_not_after)
            db.session.commit()
        case "revokeVerificationMethod" | "expireVerificationMethod":
            doc_params = payload.params
            for doc in doc_params:
                doc_from = doc['from']
                doc_did = doc['did']
                doc_vmethod_id = doc['vMethodId']
                doc_not_after = doc['notAfter']
                if payload.method == "revokeVerificationMethod":
                    doc_not_after = None

                full_vmethod_id = f"{doc_did}#{doc_vmethod_id}"
                vrelationship_repo = VerificationRelationshipRepository()
                vrel = vrelationship_repo.get(id=full_vmethod_id)
                vrelationship_repo.update(commit=False, id=vrel.id, notafter=doc_not_after)
            db.session.commit()
        case "rollVerificationMethod":
            pass
        case "sendSignedTransaction":
            pass
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
    did_repo = IdentifierRepository()
    dids_count = did_repo.count(controller=controller)
    n_pages = math.ceil(dids_count / page_size)

    links = PageLinksPublic(first=f"/identifiers?page[after]=1&page[size]={page_size}",
                            prev=f"/identifiers?page[after]={max(1, page_after - 1)}&page[size]={page_size}",
                            next=f"/identifiers?page[after]={min(page_after + 1, max(n_pages, 1))}&page[size]={page_size}",
                            last=f"/identifiers?page[after]={max(n_pages, 1)}&page[size]={page_size}")

    dids = did_repo.list(controller=controller, offset=(page_after - 1) * page_size, limit=page_size)
    items = []
    for d in dids:
        items.append(DocumentItemPublic(documentId=d.id, href=f"/identifiers/{d.id}"))

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
    vmethod_repo = VerificationMethodRepository()
    vrelationship_repo = VerificationRelationshipRepository()

    identifier = did_repo.get(did)
    vmethods = vmethod_repo.list(did_controller=did)
    vrelationships = vrelationship_repo.list(identifier_did=did)

    return IdentifierPublic(
        did=identifier.did,
        context=identifier.context,
        vmethods=vmethods,
        authentication=[vrel for vrel in vrelationships if vrel.name == "authentication"],
        assertionMethod=[vrel for vrel in vrelationships if vrel.name == "assertionMethod"],
        keyAgreement=[vrel for vrel in vrelationships if vrel.name == "keyAgreement"],
        capabilityInvocation=[vrel for vrel in vrelationships if vrel.name == "capabilityInvocation"],
        capabilityDelegation=[vrel for vrel in vrelationships if vrel.name == "capabilityDelegation"]
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
