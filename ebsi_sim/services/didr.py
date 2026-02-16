from datetime import datetime

from ebsi_sim.core.db import db
from ebsi_sim.repositories.identifier import IdentifierRepository, IdentifierControllerRepository, \
    VerificationMethodRepository, VerificationRelationshipRepository


def insertDidDocument(*, did: str, baseDocument: str, vMethodId: str, publicKey: str, isSecp256k1: bool, notBefore: int, notAfter: int):
    date_not_before = datetime.fromtimestamp(notBefore)
    date_not_after = datetime.fromtimestamp(notAfter)

    did_repo = IdentifierRepository()
    did_repo.create(commit=False, did=did, context=baseDocument)

    did_controller_repo = IdentifierControllerRepository()
    did_controller_repo.create(commit=False, identifier_did=did, did_controller=did)

    full_vmethod_id = f"{did}#{vMethodId}"

    vmethod_repo = VerificationMethodRepository()
    vmethod_repo.create(commit=False, id=full_vmethod_id, did_controller=did, type="JsonWebKey2020",
                        public_key=publicKey, issecp256k1=isSecp256k1)

    vrelationship_repo = VerificationRelationshipRepository()
    vrelationship_repo.create(commit=False, identifier_did=did, name="capabilityInvocation",
                              vmethodid=full_vmethod_id, notbefore=date_not_before, notafter=date_not_after)
    db.session.commit()

def updateBaseDocument(*, did: str, baseDocument: str):
    did_repo = IdentifierRepository()
    did_repo.update(commit=False, id=did, context=baseDocument)
    db.session.commit()

def addController(*, did: str, controller: str):
    did_controller_repo = IdentifierControllerRepository()
    did_controller_repo.create(commit=False, identifier_did=did, did_controller=controller)
    db.session.commit()

def revokeController(*, did: str, controller: str):
    did_controller_repo = IdentifierControllerRepository()
    controllers = did_controller_repo.list(identifier_did=did, did_controller=controller)
    if len(controllers) == 1:
        did_controller_repo.delete(commit=False, id=controllers[0].id)
    db.session.commit()

def addVerificationMethod(*, did: str, vMethodId: str, publicKey: str, isSecp256k1: bool):
    full_vmethod_id = f"{did}#{vMethodId}"
    vmethod_repo = VerificationMethodRepository()
    vmethod_repo.create(commit=False, id=full_vmethod_id, did_controller=did, type="JsonWebKey2020",
                        public_key=publicKey, issecp256k1=isSecp256k1)
    db.session.commit()

def addVerificationRelationship(*, did: str, name: str, vMethodId: str, notBefore: int, notAfter: int):
    not_before_date = datetime.fromtimestamp(notBefore)
    not_after_date = datetime.fromtimestamp(notAfter)

    full_vmethod_id = f"{did}#{vMethodId}"
    vrelationship_repo = VerificationRelationshipRepository()
    vrelationship_repo.create(commit=False, identifier_did=did, name=name,
                              vmethodid=full_vmethod_id,
                              notbefore=not_before_date, notafter=not_after_date)
    db.session.commit()

def revokeVerificationMethod(*, did: str, vMethodId: str, notAfter: int):
    not_after_date = datetime.fromtimestamp(notAfter)
    if not_after_date >= datetime.now():
        raise Exception("Cannot revoke a method with date in the future")

    full_vmethod_id = f"{did}#{vMethodId}"
    vmethod_repo = VerificationMethodRepository()
    vmethod = vmethod_repo.get(id=full_vmethod_id)
    vmethod_repo.update(commit=False, id=vmethod.id, notafter=not_after_date)
    db.session.commit()

def expireVerificationMethod(*, did: str, vMethodId: str, notAfter: int):
    not_after_date = datetime.fromtimestamp(notAfter)
    if not_after_date < datetime.now():
        raise Exception("Cannot set expiration of a method with date in the past")

    full_vmethod_id = f"{did}#{vMethodId}"
    vmethod_repo = VerificationMethodRepository()
    vmethod = vmethod_repo.get(id=full_vmethod_id)
    vmethod_repo.update(commit=False, id=vmethod.id, notafter=not_after_date)
    db.session.commit()