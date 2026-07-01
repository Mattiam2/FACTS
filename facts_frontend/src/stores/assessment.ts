import type {AssessedArticleInfo, AssessmentInfo, EbsiAssessmentDocument, IndexedAssessment} from "@/types";
import {defineStore} from 'pinia'
import FactsAssessmentRepo from '@/repositories/facts_assessment.ts'

export const useAssessmentStore = defineStore('assessment', {
    state: () => ({
        assessments: [] as IndexedAssessment[],
        assessment: undefined as EbsiAssessmentDocument | undefined,
    }),
    actions: {
        async loadAssessment(assessmentId: string) {
            const response = await FactsAssessmentRepo.getAssessment(assessmentId)
            this.assessment = response?.data
        },
        async getAssessment(assessmentId: string): Promise<EbsiAssessmentDocument> {
            const response = await FactsAssessmentRepo.getAssessment(assessmentId)
            return response?.data
        },
        async loadAssessmentsByArticle(articleId: string) {
            const response = await FactsAssessmentRepo.getAssessments(articleId)
            this.assessments = response?.data ?? []
        },
        async getAssessmentsByArticleUrl(articleUrl: string) {
            const response = await FactsAssessmentRepo.getAssessments(undefined, articleUrl)
            return response?.data
        },
        async loadAssessments() {
            const response = await FactsAssessmentRepo.getAssessments()
            this.assessments = response?.data ?? []
        },
        async createAssessmentTransaction(factsAccessToken: string, ethAddress: string, assessedArticle: AssessedArticleInfo, assessment: AssessmentInfo) {
            if (!factsAccessToken) {
                return
            }
            if (!ethAddress) {
                return
            }
            const response = await FactsAssessmentRepo.createAssessmentTransaction(factsAccessToken, ethAddress, assessedArticle, assessment)
            console.log("R" + response)
            return response?.data
        },
        async confirmAssessmentTransaction(factsAccessToken: string, assessmentId: string, signedTransaction: {}) {
            if (!factsAccessToken) {
                return
            }
            const response = await FactsAssessmentRepo.confirmAssessmentTransaction(factsAccessToken, assessmentId, signedTransaction)
            return response?.data
        }
    },
    persist: false,
})
