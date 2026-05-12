import type {FactsSubjectCredential} from "@/types";

function extractSubjectCredential(vc: string) {
    const vcData = JSON.parse(atob(vc.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))).vc

    if (!vcData.type.includes('VerifiableCredential') || !vcData.type.includes('FACTSFactCheckerCredential') && !vcData.type.includes('FACTSPublisherCredential')) {
        //this.addToastMessage('Invalid Verifiable Presentation type', 'error')
    }
    const credentialSubject = vcData?.credentialSubject as FactsSubjectCredential
    if (credentialSubject) {
        if (vcData.type.includes('FACTSPublisherCredential')) {
            credentialSubject.role = "PUBLISHER"
        } else if (vcData.type.includes('FACTSFactCheckerCredential')) {
            credentialSubject.role = "FACT CHECKER"
        }
    }
    return credentialSubject
}

export {extractSubjectCredential}