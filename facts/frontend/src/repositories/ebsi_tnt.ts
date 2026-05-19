import ebsiClient from '@/repositories/ebsi_base.ts'

export default {

    async createTntTransaction(accessToken: string, payload: any) {
        try {
            return await ebsiClient.post('/track-and-trace/jsonrpc', payload,
                {
                    headers: {
                        "Content-type": "application/json",
                        "Authorization": `Bearer ${accessToken}`,
                    }
                }
            )
        } catch (error: any) {
            throw new Error(error.response?.data?.detail ?? "Error while creating EBSI TNT transaction", {cause: error})
        }
    },

    async confirmTntTransaction(accessToken: string, signedTransaction: {}) {
        try {
            return await ebsiClient.post(`/track-and-trace/jsonrpc`, signedTransaction,
                {
                    headers: {
                        "Content-type": "application/json",
                        "Authorization": `Bearer ${accessToken}`,
                    }
                }
            )
        } catch (error: any) {
            throw new Error(error.response?.data?.detail ?? "Error while confirming EBSI TNT transaction", {cause: error})
        }
    }

}