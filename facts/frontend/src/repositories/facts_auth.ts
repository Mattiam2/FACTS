import factsClient from '@/repositories/facts_base.ts'

export default {

    async authenticate(vpToken: string, scope: string) {
        try {
            return await factsClient.post('/auth/token', {
                "vp_token": vpToken,
                scope,
            })
        } catch (error: any) {
            throw new Error(error.response?.data?.detail ?? "Error while authenticating on FACTS", {cause: error})
        }
    },

}