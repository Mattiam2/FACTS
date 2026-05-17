import type {FactsSubjectCredential} from "@/types";

function extractSubjectCredential(vc: string) {
    const vcData = JSON.parse(atob(vc.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))).vc

    if (!vcData.type.includes('VerifiableCredential') || !vcData.type.includes('FACTSFactCheckerCredential') && !vcData.type.includes('FACTSPublisherCredential')) {
        //this.addToastMessage('Invalid Verifiable Presentation type', 'error')
    }
    const credentialSubject = vcData?.credentialSubject as FactsSubjectCredential
    if (credentialSubject) {
        if (vcData.type.includes('FACTSPublisherCredential')) {
            credentialSubject.role = "publisher"
        } else if (vcData.type.includes('FACTSFactCheckerCredential')) {
            credentialSubject.role = "factChecker"
        }
    }
    return credentialSubject
}

function sleep(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// The formatting function
function formatDate(dateString: string) {
    if (!dateString) {return ''}

    const date = new Date(dateString)

    // Use modern JS Intl to format exactly to dd/mm/yyyy, hh:mm
    return new Intl.DateTimeFormat('it-IT', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false // Ensures 24-hour format
    }).format(date).replace(',', '')
}

export {extractSubjectCredential, formatDate, sleep}