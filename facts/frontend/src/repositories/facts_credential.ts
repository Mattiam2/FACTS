import factsClient from '@/repositories/facts_base.ts'

export default {
    async requestPublisherCredential(credentialReq: {}) {
        let response = undefined
        try {
            response = await factsClient.post(`/credentials/publisher_vc`, credentialReq)
        } catch (error) {
            console.log(error)
        }
        return response
    },
    async requestFactCheckerCredential(credentialReq: {}) {
        let response = undefined
        try {
            response = await factsClient.post(`/credentials/factchecker_vc`, credentialReq)
        } catch (error) {
            console.log(error)
        }
        return response
    }

}