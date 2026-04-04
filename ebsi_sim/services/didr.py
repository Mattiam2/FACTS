import json
from datetime import datetime

from fastapi import Depends
from web3 import Web3
from web3.contract import Contract

from ebsi_sim.core.config import settings
from ebsi_sim.core.exceptions import AuthError, NotFoundError, RequestError
from ebsi_sim.models.didr import Identifier, VerificationMethod
from ebsi_sim.repositories.didr import IdentifierRepository, IdentifierControllerRepository, \
    VerificationMethodRepository, VerificationRelationshipRepository
from ebsi_sim.schemas import JsonRpcCreate
from ebsi_sim.utils import User, check_scopes, build_unsigned_transaction, exec_signed_transaction


class DidrServiceError(Exception):
    pass

class DidrServiceAuthError(DidrServiceError, AuthError):
    pass

class DidrServiceNotFoundError(DidrServiceError, NotFoundError):
    pass

class DidrServiceRequestError(DidrServiceError, RequestError):
    pass

class DidrService:
    eth_contract: type[Contract]
    identifier_repository: IdentifierRepository
    identifier_controller_repository: IdentifierControllerRepository
    verification_method_repository: VerificationMethodRepository
    verification_relationship_repository: VerificationRelationshipRepository

    def __init__(self, identifier_repository: IdentifierRepository = Depends(),
                 identifier_controller_repository: IdentifierControllerRepository = Depends(),
                 verification_method_repository: VerificationMethodRepository = Depends(),
                 verification_relationship_repository: VerificationRelationshipRepository = Depends()):
        self.identifier_repository = identifier_repository
        self.identifier_controller_repository = identifier_controller_repository
        self.verification_method_repository = verification_method_repository
        self.verification_relationship_repository = verification_relationship_repository

        didr_abi = json.load(open("ebsi_sim/includes/abi_didr.json", "r"))
        self.eth_contract = Web3().eth.contract(abi=didr_abi)

    def get_did_document(self, did: str) -> Identifier | None:
        return self.identifier_repository.get(did)

    def count_did_documents(self, *, controller=None, **filters):
        return self.identifier_repository.count(controller=controller, **filters)

    def list_did_documents(self, *, offset=None, limit=None, order_by=None, controller=None, **filters):
        return self.identifier_repository.list(offset=offset, limit=limit, order_by=order_by, controller=controller,
                                               **filters)

    def get_verification_method(self, v_method_id: str) -> VerificationMethod | None:
        return self.verification_method_repository.get(v_method_id)

    def list_verification_methods(self, *, offset=None, limit=None, order_by=None, **filters) -> list[VerificationMethod]:
        return self.verification_method_repository.list(offset=offset, limit=limit, order_by=order_by, **filters)

    def insert_did_document(self, *, did: str, base_document: str, v_method_id: str, public_key: bytes | str, is_secp256k1: bool,
                          not_before: int, not_after: int):
        date_not_before = datetime.fromtimestamp(not_before)
        date_not_after = datetime.fromtimestamp(not_after)

        self.identifier_repository.create(did=did, context=base_document)
        self.identifier_controller_repository.create(identifier_did=did, did_controller=did)

        full_vmethod_id = f"{did}#{v_method_id}"

        if isinstance(public_key, bytes):
            public_key = "0x" + public_key.hex()

        self.verification_method_repository.create(id=full_vmethod_id, did_controller=did,
                                                   type="JsonWebKey2020",
                                                   public_key=public_key, issecp256k1=is_secp256k1, notafter=date_not_after)

        self.verification_relationship_repository.create(identifier_did=did, name="capabilityInvocation",
                                                         vmethodid=full_vmethod_id, notbefore=date_not_before,
                                                         notafter=date_not_after)

        self.verification_relationship_repository.create(identifier_did=did, name="authentication",
                                                         vmethodid=full_vmethod_id, notbefore=date_not_before,
                                                         notafter=date_not_after)

    def update_base_document(self, *, did: str, base_document: str):
        self.identifier_repository.update(id=did, context=base_document)

    def add_controller(self, *, did: str, controller: str):
        self.identifier_controller_repository.create(identifier_did=did, did_controller=controller)

    def revoke_controller(self, *, did: str, controller: str):
        controllers = self.identifier_controller_repository.list(identifier_did=did, did_controller=controller)
        if len(controllers) == 1:
            self.identifier_controller_repository.delete(id=controllers[0].id)

    def add_verification_method(self, *, did: str, v_method_id: str, public_key: bytes | str, is_secp256k1: bool):
        full_vmethod_id = f"{did}#{v_method_id}"
        if isinstance(public_key, bytes):
            public_key = "0x" + public_key.hex()
        self.verification_method_repository.create(id=full_vmethod_id, did_controller=did,
                                                   type="JsonWebKey2020",
                                                   public_key=public_key, issecp256k1=is_secp256k1)

    def add_verification_relationship(self, *, did: str, name: str, v_method_id: str, not_before: int, not_after: int):
        not_before_date = datetime.fromtimestamp(not_before)
        not_after_date = datetime.fromtimestamp(not_after)

        full_vmethod_id = f"{did}#{v_method_id}"
        self.verification_relationship_repository.create(identifier_did=did, name=name,
                                                         vmethodid=full_vmethod_id,
                                                         notbefore=not_before_date, notafter=not_after_date)

    def revoke_verification_method(self, *, did: str, v_method_id: str, not_after: int):
        not_after_date = datetime.fromtimestamp(not_after)
        if not_after_date >= datetime.now():
            raise DidrServiceRequestError("Cannot revoke a method with date in the future")

        full_vmethod_id = f"{did}#{v_method_id}"
        vmethod = self.verification_method_repository.get(id=full_vmethod_id)
        if not vmethod:
            raise DidrServiceNotFoundError("Verification method not found")
        self.verification_method_repository.update(id=vmethod.id, notafter=not_after_date)

    def expire_verification_method(self, *, did: str, v_method_id: str, not_after: int):
        not_after_date = datetime.fromtimestamp(not_after)
        if not_after_date < datetime.now():
            raise DidrServiceRequestError("Cannot set expiration of a method with date in the past")

        full_vmethod_id = f"{did}#{v_method_id}"
        vmethod = self.verification_method_repository.get(id=full_vmethod_id)
        if not vmethod:
            raise DidrServiceNotFoundError("Verification method not found")
        self.verification_method_repository.update(id=vmethod.id, notafter=not_after_date)

    def _check_scope(self, current_user: User, method: str):
        is_authorized = check_scopes(current_user, method, {
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
            raise DidrServiceAuthError("Forbidden method")

    def _check_did_access(self, current_user: User, payload: JsonRpcCreate):
        method = payload.method
        subject_did: str | None = payload.params[0].get("did", None) if len(payload.params) > 0 else None
        if method not in ("insertDidDocument", "updateBaseDocument", "addService", "revokeService", "addController",
                              "revokeController", "addVerificationMethod", "addVerificationRelationship",
                              "revokeVerificationMethod", "expireVerificationMethod", "rollVerificationMethod"):
            raise DidrServiceRequestError("Method not allowed")

        if subject_did is not None and subject_did != current_user.sub:
            subject_did: str
            if method == "insertDidDocument":
                raise DidrServiceAuthError("Forbidden DID")
            sub_identifier = self.get_did_document(subject_did)
            if not sub_identifier:
                raise DidrServiceRequestError("Subject identifier not found in DID Register")
            controllers = sub_identifier.controllers
            if current_user.sub not in [c.did for c in controllers]:
                raise DidrServiceAuthError("Forbidden DID")

    def handle_rpc(self, current_user: User, payload: JsonRpcCreate):
        try:
            params = payload.params[0] if len(payload.params) > 0 else {}
            self._check_scope(current_user, payload.method)
            if payload.method != "sendSignedTransaction":
                self._check_did_access(current_user, payload)
                json_rpc_result = build_unsigned_transaction(self.eth_contract, settings.ETH_ADDRESS, payload.method, params)
            else:
                json_rpc_result = exec_signed_transaction(current_user, self.eth_contract, settings.ETH_ADDRESS, self,
                                                          params['unsignedTransaction'],
                                                          params['signedRawTransaction'])
        except DidrServiceError:
            raise
        except Exception:
            raise DidrServiceError("Internal error")
        else:
            return json_rpc_result