import ebsiClient from '@/repositories/ebsi_base.ts'

export default {

    async createTntTransaction(accessToken: string, payload: any) {
        return await ebsiClient.post('/track-and-trace/jsonrpc', payload,
            {
                headers: {
                    "Content-type": "application/json",
                    "Authorization": `Bearer ${accessToken}`,
                }
            }
        )
    },

    async confirmTntTransaction(accessToken: string, signedTransaction: {}) {
        return await ebsiClient.post(`/track-and-trace/jsonrpc`, signedTransaction,
            {
                headers: {
                    "Content-type": "application/json",
                    "Authorization": `Bearer ${accessToken}`,
                }
            }
        )
    }

}