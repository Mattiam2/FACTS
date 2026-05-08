import factsClient from '@/repositories/facts_base.ts'

export default {

    async authenticate(vpToken: string, scope: string) {
        return await factsClient.post('/auth/token', {
            "vp_token": vpToken,
            scope,
        })
    },

}