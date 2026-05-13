import type {AssessedArticleInfo, AssessmentInfo, FactsSubjectCredential} from "@/types";
import {defineStore} from 'pinia'
import {type Transaction, Web3} from "web3";
import EbsiAuthRepo from '@/repositories/ebsi_auth.ts'
import EbsiDidrRepo from '@/repositories/ebsi_didr.ts'

export const useWalletStore = defineStore('wallet', {
    state: () => ({
        ebsiAccessToken: undefined as string | undefined,
        ethWallet: {ethAddress: undefined, privateKey: undefined, publicKey: undefined} as {
            ethAddress?: string,
            privateKey?: string,
            publicKey?: string
        },
    }),
    actions: {
        async requestEbsiAccessToken(vpToken: string, scope: string) {
            const response = await EbsiAuthRepo.authenticate(vpToken, scope)
            this.ebsiAccessToken = response?.data.access_token
        },
        async linkWallet(ethAddress: string, ethPrivateKey: string) {
            const web3 = new Web3()
            const account = web3.eth.accounts.privateKeyToAccount(ethPrivateKey);
            if (account.address.toLowerCase() != ethAddress.toLowerCase()) {
                throw new Error("Invalid address");
            }
            this.ethWallet.ethAddress = ethAddress
            this.ethWallet.privateKey = ethPrivateKey
            this.ethWallet.publicKey = web3.eth.accounts.privateKeyToPublicKey(ethPrivateKey, false);
        },
        async signTransaction(transaction: Transaction, ethPrivateKey: string) {
            const web3 = new Web3()
            transaction.gas = 103972
            const signedTx = await web3.eth.accounts.signTransaction(transaction, ethPrivateKey);

            const signedTransaction = {
                protocol: "eth",
                unsignedTransaction: transaction,
                r: signedTx.r,
                s: signedTx.s,
                v: Number.parseInt(signedTx.v),
                signedRawTransaction: signedTx.rawTransaction.slice(2),
            }
            return signedTransaction
        },
        async createDidDocumentTransaction(credentialSubject: FactsSubjectCredential, vMethodId: string) {
            if (!this.ebsiAccessToken) {
                return
            }
            if (!this.ethWallet.ethAddress) {
                return
            }
            const payloadInsertDidDocument = {
                "jsonrpc": "2.0",
                "method": "insertDidDocument",
                "params": [
                    {
                        "from": this.ethWallet.ethAddress,
                        "did": credentialSubject.id,
                        "baseDocument": "{\"@context\":[\"https://www.w3.org/ns/did/v1\",\"https://w3id.org/security/suites/jws-2020/v1\"]}",
                        vMethodId,
                        "publicKey": this.ethWallet.publicKey,
                        "isSecp256k1": true,
                        "notBefore": Date.now(),
                        "notAfter": Date.now() + 3600 * 1000,
                    }
                ],
                "id": 474
            }
            const response = await EbsiDidrRepo.createDidDocumentTransaction(this.ebsiAccessToken, payloadInsertDidDocument)
            return response?.data
        },
        async confirmDidDocumentTransaction(assessmentId: string, signedTransaction: {}) {
            if (!this.ebsiAccessToken) {
                return
            }
            if (!this.ethWallet.ethAddress) {
                return
            }
            const response = await EbsiDidrRepo.confirmDidDocumentTransaction(this.ebsiAccessToken, assessmentId, signedTransaction)
            return response?.data
        },
    },
    persist: true,
})
