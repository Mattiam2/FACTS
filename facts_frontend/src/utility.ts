import {CredibilityScore, type FactsSubjectCredential, ManipulationScore} from "@/types";

const rules = {
  required: (value: any) => !!value || 'Field is required',
  url: (value: string) => {
    try {
      new URL(value)
    } catch {
      return 'Invalid URL'
    }
    return (value.startsWith("http://") || value.startsWith("https://")) || 'URL must start with http:// or https://'
  },
}

/**
 * Extracts the subject credential from a verifiable credential (VC) token.
 *
 * @param {string} vc - The base64url-encoded JSON Web Token (JWT) representing the verifiable credential.
 * @return {FactsSubjectCredential | undefined} Returns the subject credential object with additional role information if available; otherwise, returns undefined.
 */
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

/**
 * Pauses the execution of code for a specified duration.
 *
 * @param {number} ms - The number of milliseconds to sleep.
 * @return {Promise<void>} A promise that resolves after the specified duration.
 */
function sleep(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Formats a given date string into the format dd/mm/yyyy.
 *
 * @param {string} dateString - The date string to be formatted.
 * @return {string} The formatted date string in dd/mm/yyyy format. Returns an empty string if no dateString is provided.
 */
function formatDate(dateString: string) {
    if (!dateString) {return ''}

    const date = new Date(dateString)

    // Use modern JS Intl to format exactly to dd/mm/yyyy, hh:mm
    return new Intl.DateTimeFormat('it-IT', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: undefined,
        minute: undefined,
        hour12: false // Ensures 24-hour format
    }).format(date).replace(',', '')
}

/**
 * Provides a descriptive label for a given credibility score.
 *
 * @param {number} average - The numerical credibility score to evaluate.
 * @return {string} A descriptive string corresponding to the credibility score.
 */
function getCredibilityDescription(average: number) {
  switch (average) {
    case CredibilityScore.FALSE: {
      return 'False'
    }
    case CredibilityScore.PARTIALLY_FALSE: {
      return 'Partially False'
    }
    case CredibilityScore.MISSING_CONTEXT: {
      return 'Missing Context'
    }
    case CredibilityScore.SUBJECTIVE: {
      return 'Subjective'
    }
    case CredibilityScore.TRUE: {
      return 'True'
    }
  }
  return ''
}

/**
 * Returns a descriptive label for a given manipulation score.
 *
 * @param {number} average - The numerical manipulation score to evaluate.
 * @return {string} A descriptive string corresponding to the manipulation score.
 */
function getManipulationDescription(average: number) {
  switch (average) {
    case ManipulationScore.TOTALLY_MANIPULATED: {
      return 'Completely Manipulated'
    }
    case ManipulationScore.HEAVILY_MANIPULATED: {
      return 'Heavily Manipulated'
    }
    case ManipulationScore.PARTIALLY_MANIPULATED: {
      return 'Partially Manipulated'
    }
    case ManipulationScore.MINOR_EDITS: {
      return 'Minor Edits'
    }
    case ManipulationScore.AUTHENTIC: {
      return 'Authentic'
    }
  }
  return ''
}

export {extractSubjectCredential, formatDate, getCredibilityDescription, getManipulationDescription, rules, sleep}