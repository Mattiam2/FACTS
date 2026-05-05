from fastapi import APIRouter, Depends
from sqlmodel import SQLModel

from facts.src.repositories.ebsi_issuer import IssuerRepository

# TODO: In reality for FACTS Issuer!

class CredentialSubject(SQLModel):
    subject_did: str
    company_name: str
    company_address: str
    company_vat: str
    company_website: str
    company_email: str
    company_country: str

class PublisherSubject(CredentialSubject):
    authorized_hosts: list[str]

class FactCheckerSubject(CredentialSubject):
    specialization: str | None
    accredited_by: str | None

router = APIRouter(prefix="/credentials", tags=["credentials"])

@router.post("/publisher_vc")
def request_vc_publisher(payload: PublisherSubject, issuer_repo: IssuerRepository = Depends()):
    subject_did = payload.subject_did
    credential_subject = payload.model_dump(mode="json")
    credential_subject.pop("subject_did")
    return issuer_repo.request_vc({
        "subject_did": subject_did,
        "credential_subject": credential_subject,
        "credential_type": ['VerifiableCredential', 'VerifiableAuthorisationToOnboard', 'FACTSPublisherCredential']
    })

@router.post("/factchecker_vc")
def request_vc_factchecker(payload: FactCheckerSubject, issuer_repo: IssuerRepository = Depends()):
    subject_did = payload.subject_did
    credential_subject = payload.model_dump(mode="json")
    credential_subject.pop("subject_did")
    return issuer_repo.request_vc({
        "subject_did": subject_did,
        "credential_subject": credential_subject,
        "credential_type": ['VerifiableCredential', 'VerifiableAuthorisationToOnboard', 'FACTSFactCheckerCredential']
    })