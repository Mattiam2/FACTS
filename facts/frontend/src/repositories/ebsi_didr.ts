import ebsiClient from '@/repositories/ebsi_base.ts'



const payloadInsertDidDocument = {
    "jsonrpc": "2.0",
    "method": "insertDidDocument",
    "params": [
        {
            "from": undefined as string | undefined,
            "did": undefined as string | undefined,
            "baseDocument": "{\"@context\":[\"https://www.w3.org/ns/did/v1\",\"https://w3id.org/security/suites/jws-2020/v1\"]}",
            "vMethodId": undefined as string | undefined,
            "publicKey": undefined as string | undefined,
            "isSecp256k1": true,
            "notBefore": undefined as number | undefined,
            "notAfter": undefined as number | undefined,
        }
    ],
    "id": 474
}

const payloadSendSignedTransaction = {
    "jsonrpc": "2.0",
    "method": "sendSignedTransaction",
    "id": 1,
    "params": [
        {
            "protocol": "eth",
            "unsignedTransaction": undefined as object | undefined,
            "r": undefined as string | undefined,
            "s": undefined as string | undefined,
            "v": undefined as number | undefined,
            "signedRawTransaction": undefined as string | undefined,
        }
    ]
}


export default {

    async createDidDocumentTransaction(accessToken: string, payload: any) {
        return await ebsiClient.post('/did-registry/jsonrpc', payload,
            {
                headers: {
                    "Content-type": "application/json",
                    "Authorization": `Bearer ${accessToken}`,
                }
            }
        )
    },

    async confirmDidDocumentTransaction(accessToken: string, articleId: string, signedTransaction: {}) {
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