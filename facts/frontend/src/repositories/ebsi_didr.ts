import ebsiClient from '@/repositories/ebsi_base.ts'

export default {

    async createDidrTransaction(accessToken: string, payload: any) {
        return await ebsiClient.post('/did-registry/jsonrpc', payload,
            {
                headers: {
                    "Content-type": "application/json",
                    "Authorization": `Bearer ${accessToken}`,
                }
            }
        )
    },

    async confirmDidrTransaction(accessToken: string, signedTransaction: {}) {
        return await ebsiClient.post(`/did-registry/jsonrpc`, signedTransaction,
            {
                headers: {
                    "Content-type": "application/json",
                    "Authorization": `Bearer ${accessToken}`,
                }
            }
        )
    }

}