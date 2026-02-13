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

    return True