from fastapi import APIRouter, Depends
from sqlmodel import SQLModel

from facts_publish.src.repositories.ebsi_issuer import IssuerRepository


class CredentialSubject(SQLModel):
    subject_did: str
    company_name: str
    company_address: str
    company_vat: str

router = APIRouter(prefix="/credentials")

@router.post("/")
def request_vc(payload: CredentialSubject, issuer_repo: IssuerRepository = Depends()):
    return issuer_repo.request_vc({
        "subject_did": payload.subject_did,
        "credential_subject":{
            "company_name": payload.company_name,
            "company_address": payload.company_address,
            "company_vat": payload.company_vat
        },
        "credential_type": ['VerifiableCredential', 'FACTSPublisherCredential']
    })
