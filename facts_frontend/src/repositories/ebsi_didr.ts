import ebsiClient from '@/repositories/ebsi_base.ts'

export default {

    async createDidrTransaction(accessToken: string, payload: any) {
        try {
            return await ebsiClient.post('/did-registry/jsonrpc', payload,
                {
                    headers: {
                        "Content-type": "application/json",
                        "Authorization": `Bearer ${accessToken}`,
                    }
                }
            )
        }catch(error: any){
            throw new Error(error.response?.data?.detail ?? "Error while creating EBSI DIDR transaction", {cause: error})
        }
    },

    async confirmDidrTransaction(accessToken: string, signedTransaction: {}) {
        try {
            return await ebsiClient.post(`/did-registry/jsonrpc`, signedTransaction,
                {
                    headers: {
                        "Content-type": "application/json",
                        "Authorization": `Bearer ${accessToken}`,
                    }
                }
            )
        }catch(error: any){
            throw new Error(error.response?.data?.detail ?? "Error while confirming EBSI DIDR transaction", {cause: error})
        }
    }

}