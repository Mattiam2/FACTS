import type {FactsSubjectCredential} from "@/types";
import {defineStore} from 'pinia'
import {type Transaction, Web3} from "web3";
import EbsiAuthRepo from '@/repositories/ebsi_auth.ts'
import EbsiDidrRepo from '@/repositories/ebsi_didr.ts'
import EbsiTntRepo from '@/repositories/ebsi_tnt.ts'

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
            this.ethWallet.publicKey = web3.eth.accounts.privateKeyToPublicKey(ethPrivateKey, false).replace("0x", "0x04");
        },
        async signTransaction(transaction: Transaction) {
            if (!this.ethWallet.privateKey) {
                throw new Error("Wallet not linked")
            }
            const web3 = new Web3()
            transaction.gas = 103972
            const signedTx = await web3.eth.accounts.signTransaction(transaction, this.ethWallet.privateKey);

            return {
                protocol: "eth",
                unsignedTransaction: transaction,
                r: signedTx.r,
                s: signedTx.s,
                v: Number.parseInt(signedTx.v),
                signedRawTransaction: signedTx.rawTransaction.slice(2),
            }
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
                        "notBefore": Math.round(Date.now() / 1000),
                        "notAfter": Math.round((Date.now() + 3600 * 24 * 365 * 1000) / 1000),
                    }
                ],
                "id": 474
            }
            const response = await EbsiDidrRepo.createDidrTransaction(this.ebsiAccessToken, payloadInsertDidDocument)
            return response?.data
        },
        async confirmDidrTransaction(signedTransaction: {}) {
            if (!this.ebsiAccessToken) {
                return
            }
            if (!this.ethWallet.ethAddress) {
                return
            }
            const payloadDidr = {
                "jsonrpc": "2.0",
                "method": "sendSignedTransaction",
                "params": [
                    signedTransaction
                ],
                "id": 575
            }
            const response = await EbsiDidrRepo.confirmDidrTransaction(this.ebsiAccessToken, payloadDidr)
            return response?.data
        },
        async createVerificationMethodTransaction(credentialSubject: FactsSubjectCredential, vMethodId: string, publicKey: string, isSecp256k1: boolean) {
            if (!this.ebsiAccessToken) {
                return
            }
            if (!this.ethWallet.ethAddress) {
                return
            }
            const payloadAddVMethod = {
                "jsonrpc": "2.0",
                "method": "addVerificationMethod",
                "params": [
                    {
                        "from": this.ethWallet.ethAddress,
                        "did": credentialSubject.id,
                        vMethodId,
                        publicKey,
                        isSecp256k1
                    }
                ],
                "id": 575
            }
            const response = await EbsiDidrRepo.createDidrTransaction(this.ebsiAccessToken, payloadAddVMethod)
            return response?.data
        },
        async createVerificationRelationshipTransaction(credentialSubject: FactsSubjectCredential, vMethodId: string, relationshipType: string) {
            if (!this.ebsiAccessToken) {
                return
            }
            if (!this.ethWallet.ethAddress) {
                return
            }
            const payloadAddVMethod = {
                "jsonrpc": "2.0",
                "method": "addVerificationRelationship",
                "params": [
                    {
                        "from": this.ethWallet.ethAddress,
                        "did": credentialSubject.id,
                        "name": relationshipType,
                        vMethodId,
                        "notBefore": Math.round(Date.now() / 1000),
                        "notAfter": Math.round((Date.now() + 3600 * 24 * 365 * 10 * 1000) / 1000),
                    }
                ],
                "id": 575
            }
            const response = await EbsiDidrRepo.createDidrTransaction(this.ebsiAccessToken, payloadAddVMethod)
            return response?.data
        },
        async createAuthoriseDidTransaction(credentialSubject: FactsSubjectCredential) {
            if (!this.ebsiAccessToken) {
                return
            }
            if (!this.ethWallet.ethAddress) {
                return
            }
            const payloadAuthoriseDid = {
                "jsonrpc": "2.0",
                "method": "authoriseDid",
                "params": [
                    {
                        "from": this.ethWallet.ethAddress,
                        "senderDid": credentialSubject.id,
                        "authorisedDid": credentialSubject.id,
                        "whiteList": "0x01"
                    }
                ],
                "id": 575
            }
            const response = await EbsiTntRepo.createTntTransaction(this.ebsiAccessToken, payloadAuthoriseDid)
            return response?.data
        },
        async confirmTntTransaction(signedTransaction: {}) {
            if (!this.ebsiAccessToken) {
                return
            }
            if (!this.ethWallet.ethAddress) {
                return
            }
            const payloadTnt = {
                "jsonrpc": "2.0",
                "method": "sendSignedTransaction",
                "params": [
                    signedTransaction
                ],
                "id": 575
            }
            const response = await EbsiTntRepo.confirmTntTransaction(this.ebsiAccessToken, payloadTnt)
            return response?.data
        },
    },
    persist: true,
})
