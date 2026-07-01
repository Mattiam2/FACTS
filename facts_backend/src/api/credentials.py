from fastapi import APIRouter, Depends

from facts_backend.src.schemas.issuer import PublisherSubject, FactCheckerSubject, CredentialCreate
from facts_backend.src.services.credential import CredentialService

router = APIRouter(prefix="/credentials", tags=["credentials"])


@router.post("/publisher_vc")
def request_vc_publisher(payload: PublisherSubject, credential_service: CredentialService = Depends()):
    subject_did = payload.subject_did
    credential_subject = payload.model_dump(mode="json")
    credential_subject.pop("subject_did")
    credential_payload = CredentialCreate.model_validate({
        "subject_did": subject_did,
        "credential_subject": credential_subject,
        "credential_type": ['VerifiableCredential', 'VerifiableAuthorisationToOnboard', 'FACTSPublisherCredential']
    })
    return credential_service.request_credential(credential_payload)


@router.post("/factchecker_vc")
def request_vc_factchecker(payload: FactCheckerSubject, credential_service: CredentialService = Depends()):
    subject_did = payload.subject_did
    credential_subject = payload.model_dump(mode="json")
    credential_subject.pop("subject_did")
    credential_payload = CredentialCreate.model_validate({
        "subject_did": subject_did,
        "credential_subject": credential_subject,
        "credential_type": ['VerifiableCredential', 'VerifiableAuthorisationToOnboard', 'FACTSFactCheckerCredential']
    })
    return credential_service.request_credential(credential_payload)
