import type {FactsSubjectCredential} from "@/types";
import {defineStore} from 'pinia'
import FactsAuthRepo from '@/repositories/facts_auth.ts'
import {extractSubjectCredential} from "@/utility.ts";

export const useAuthStore = defineStore('auth', {
    state: () => ({
        factsAccessToken: undefined as string | undefined,
        factsCredentialSubject: undefined as FactsSubjectCredential | undefined,
    }),
    actions: {
        async requestFactsAccessToken(vpToken: string, scope: string) {
            const response = await FactsAuthRepo.authenticate(vpToken, scope)
            this.factsAccessToken = response.data.access_token
        },
        loadSubjectCredential(vc: string) {
            this.factsCredentialSubject = extractSubjectCredential(vc)
        }
    },
    persist: true,
})
