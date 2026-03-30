from datetime import datetime

from fastapi import Depends

from ebsi_sim.models.didr import Identifier, VerificationMethod
from ebsi_sim.repositories.didr import IdentifierRepository, IdentifierControllerRepository, \
    VerificationMethodRepository, VerificationRelationshipRepository


class DidrServiceException(Exception):
    pass


class DidrService:
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
                          notBefore: int, notAfter: int):
        date_not_before = datetime.fromtimestamp(notBefore)
        date_not_after = datetime.fromtimestamp(notAfter)

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
            publicKey = "0x" + public_key.hex()
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
            raise DidrServiceException("Cannot revoke a method with date in the future")

        full_vmethod_id = f"{did}#{v_method_id}"
        vmethod = self.verification_method_repository.get(id=full_vmethod_id)
        self.verification_method_repository.update(id=vmethod.id, notafter=not_after_date)

    def expire_verification_method(self, *, did: str, v_method_id: str, not_after: int):
        not_after_date = datetime.fromtimestamp(not_after)
        if not_after_date < datetime.now():
            raise DidrServiceException("Cannot set expiration of a method with date in the past")

        full_vmethod_id = f"{did}#{v_method_id}"
        vmethod = self.verification_method_repository.get(id=full_vmethod_id)
        self.verification_method_repository.update(id=vmethod.id, notafter=not_after_date)
