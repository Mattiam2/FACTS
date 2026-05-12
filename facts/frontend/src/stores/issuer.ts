import {defineStore} from 'pinia'
import FactsCredentialRepo from '@/repositories/facts_credential.ts'

export const useIssuerStore = defineStore('issuer', {
    actions: {
        async requestCredential(credentialRequest: {}, userRole: string) {
            let response = undefined
            if (userRole == "publisher") {
                response = await FactsCredentialRepo.requestPublisherCredential(credentialRequest)
            } else if (userRole == "factChecker") {
                response = await FactsCredentialRepo.requestFactCheckerCredential(credentialRequest)
            }
            return response?.data
        },
    },
    persist: false,
})
