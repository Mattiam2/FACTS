import type {ArticleInfo, AssessedArticleInfo, AssessmentInfo, FactsSubjectCredential} from "@/types";
import {defineStore} from 'pinia'
import AuthRepo from '@/repositories/facts_auth.ts'

export const useAppStore = defineStore('app', {
    state: () => ({
        vcToken: undefined as string | undefined,
        factsCredentialSubject: undefined as FactsSubjectCredential | undefined,
        ethWalletAddress: undefined as string | undefined,
        factsAccessToken: undefined as string | undefined,
        toastMessages: [] as { text: string, color?: string, onDismiss?: () => void }[]
    }),
    actions: {
        addToastMessage(text: string, type: 'success' | 'error' = 'success') {
            this.toastMessages.push({text, color: type})
        },
        async requestAccessToken(vpToken: string, scope: string) {
            const response = await AuthRepo.authenticate(vpToken, scope)
            this.factsAccessToken = response.data.access_token
        },
        async getArticleByUrl(articleUrl: string) {
            const response = await AuthRepo.getArticleByUrl(articleUrl)
            return response?.data
        },
        async getArticle(articleId: string) {
            const response = await AuthRepo.getArticle(articleId)
            return response?.data
        },
        async getArticles() {
            const response = await AuthRepo.getArticles()
            return response?.data
        },
        async createArticleTransaction(articleInfo: ArticleInfo) {
            if (!this.factsAccessToken) {
                return
            }
            if (!this.ethWalletAddress) {
                return
            }
            const response = await AuthRepo.createArticleTransaction(this.factsAccessToken, this.ethWalletAddress, articleInfo)
            console.log("R" + response)
            return response?.data
        },
        async confirmArticleTransaction(articleId: string, signedTransaction: {}) {
            if (!this.factsAccessToken) {
                return
            }
            if (!this.ethWalletAddress) {
                return
            }
            const response = await AuthRepo.confirmArticleTransaction(this.factsAccessToken, articleId, signedTransaction)
            return response?.data
        },
        async getAssessment(assessmentId: string) {
            const response = await AuthRepo.getAssessment(assessmentId)
            return response?.data
        },
        async getAssessments(articleId: string) {
            const response = await AuthRepo.getAssessments(articleId)
            return response?.data
        },
        async createAssessmentTransaction(assessedArticle: AssessedArticleInfo, assessment: AssessmentInfo) {
            if (!this.factsAccessToken) {
                return
            }
            if (!this.ethWalletAddress) {
                return
            }
            const response = await AuthRepo.createAssessmentTransaction(this.factsAccessToken, this.ethWalletAddress, assessedArticle, assessment)
            console.log("R" + response)
            return response?.data
        },
        async confirmAssessmentTransaction(assessmentId: string, signedTransaction: {}) {
            if (!this.factsAccessToken) {
                return
            }
            if (!this.ethWalletAddress) {
                return
            }
            const response = await AuthRepo.confirmAssessmentTransaction(this.factsAccessToken, assessmentId, signedTransaction)
            return response?.data
        },
        extractSubjectCredential(vc: string): FactsSubjectCredential {
            const vcData = JSON.parse(atob(vc.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))).vc

            if (!vcData.type.includes('VerifiableCredential') || !vcData.type.includes('FACTSFactCheckerCredential') && !vcData.type.includes('FACTSPublisherCredential')) {
                this.addToastMessage('Invalid Verifiable Presentation type', 'error')
            }
            const credentialSubject = vcData?.credentialSubject as FactsSubjectCredential
            if (credentialSubject) {
                if (vcData.type.includes('FACTSPublisherCredential')) {
                    credentialSubject.role = "PUBLISHER"
                } else if (vcData.type.includes('FACTSFactCheckerCredential')) {
                    credentialSubject.role = "FACT CHECKER"
                }
            }
            return credentialSubject
        },
    },
    persist: true,
})
