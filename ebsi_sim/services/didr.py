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

    def getDidDocument(self, did: str) -> Identifier:
        return self.identifier_repository.get(did)

    def countDidDocuments(self, *, controller=None, **filters):
        return self.identifier_repository.count(controller=controller, **filters)

    def listDidDocuments(self, *, offset=None, limit=None, order_by=None, controller=None, **filters):
        return self.identifier_repository.list(offset=offset, limit=limit, order_by=order_by, controller=controller,
                                               **filters)

    def getVerificationMethod(self, vMethodId: str) -> VerificationMethod:
        return self.verification_method_repository.get(vMethodId)

    def listVerificationMethods(self, *, offset=None, limit=None, order_by=None, **filters) -> list[VerificationMethod]:
        return self.verification_method_repository.list(offset=offset, limit=limit, order_by=order_by, **filters)

    def insertDidDocument(self, *, did: str, baseDocument: str, vMethodId: str, publicKey: str, isSecp256k1: bool,
                          notBefore: int, notAfter: int):
        date_not_before = datetime.fromtimestamp(notBefore)
        date_not_after = datetime.fromtimestamp(notAfter)

        self.identifier_repository.create(did=did, context=baseDocument)
        self.identifier_controller_repository.create(identifier_did=did, did_controller=did)

        full_vmethod_id = f"{did}#{vMethodId}"

        self.verification_method_repository.create(id=full_vmethod_id, did_controller=did,
                                                   type="JsonWebKey2020",
                                                   public_key=publicKey, issecp256k1=isSecp256k1)

        self.verification_relationship_repository.create(identifier_did=did, name="capabilityInvocation",
                                                         vmethodid=full_vmethod_id, notbefore=date_not_before,
                                                         notafter=date_not_after)

    def updateBaseDocument(self, *, did: str, baseDocument: str):
        self.identifier_repository.update(id=did, context=baseDocument)

    def addController(self, *, did: str, controller: str):
        self.identifier_controller_repository.create(identifier_did=did, did_controller=controller)

    def revokeController(self, *, did: str, controller: str):
        controllers = self.identifier_controller_repository.list(identifier_did=did, did_controller=controller)
        if len(controllers) == 1:
            self.identifier_controller_repository.delete(id=controllers[0].id)

    def addVerificationMethod(self, *, did: str, vMethodId: str, publicKey: str, isSecp256k1: bool):
        full_vmethod_id = f"{did}#{vMethodId}"
        self.verification_method_repository.create(id=full_vmethod_id, did_controller=did,
                                                   type="JsonWebKey2020",
                                                   public_key=publicKey, issecp256k1=isSecp256k1)

    def addVerificationRelationship(self, *, did: str, name: str, vMethodId: str, notBefore: int, notAfter: int):
        not_before_date = datetime.fromtimestamp(notBefore)
        not_after_date = datetime.fromtimestamp(notAfter)

        full_vmethod_id = f"{did}#{vMethodId}"
        self.verification_relationship_repository.create(identifier_did=did, name=name,
                                                         vmethodid=full_vmethod_id,
                                                         notbefore=not_before_date, notafter=not_after_date)

    def revokeVerificationMethod(self, *, did: str, vMethodId: str, notAfter: int):
        not_after_date = datetime.fromtimestamp(notAfter)
        if not_after_date >= datetime.now():
            raise DidrServiceException("Cannot revoke a method with date in the future")

        full_vmethod_id = f"{did}#{vMethodId}"
        vmethod = self.verification_method_repository.get(id=full_vmethod_id)
        self.verification_method_repository.update(id=vmethod.id, notafter=not_after_date)

    def expireVerificationMethod(self, *, did: str, vMethodId: str, notAfter: int):
        not_after_date = datetime.fromtimestamp(notAfter)
        if not_after_date < datetime.now():
            raise DidrServiceException("Cannot set expiration of a method with date in the past")

        full_vmethod_id = f"{did}#{vMethodId}"
        vmethod = self.verification_method_repository.get(id=full_vmethod_id)
        self.verification_method_repository.update(id=vmethod.id, notafter=not_after_date)
