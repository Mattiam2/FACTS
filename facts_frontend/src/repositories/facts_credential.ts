import factsClient from '@/repositories/facts_base.ts'

export default {
    async requestPublisherCredential(credentialReq: {}) {
        try {
            return await factsClient.post(`/credentials/publisher_vc`, credentialReq)
        } catch (error: any) {
            throw new Error(error.response?.data?.detail ?? "Error requesting credential", { cause: error })
        }
    },
    async requestFactCheckerCredential(credentialReq: {}) {
        try {
            return await factsClient.post(`/credentials/factchecker_vc`, credentialReq)
        } catch (error: any) {
            throw new Error(error.response?.data?.detail ?? "Error requesting credential", { cause: error })
        }
    }

}