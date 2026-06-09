import type {AssessedArticleInfo, AssessmentInfo} from "@/types";
import factsClient from '@/repositories/facts_base.ts'

export default {

    async getAssessment(assessmentId: string) {
        try {
            return await factsClient.get(`/assessments/${assessmentId}`)
        } catch (error: any) {
            if(error.response?.status == 404){
                return undefined
            }
            throw new Error(error.response?.data?.detail ?? "Error while fetching assessment", {cause: error})
        }
    },
    async getAssessments(articleId?: string, articleUrl?: string) {
        try {
            const params: { [key: string]: string } = {}
            if (articleId) {
                params['article_hash'] = articleId
            }
            if (articleUrl) {
                params['article_url'] = articleUrl
            }
            return await factsClient.get('/assessments', {params})
        } catch (error: any) {
            if(error.response?.status == 404){
                return undefined
            }
            throw new Error(error.response?.data?.detail ?? "Error while fetching assessments", {cause: error})
        }
    },

    async createAssessmentTransaction(accessToken: string, ethAddress: string, assessedArticle: AssessedArticleInfo, assessment: AssessmentInfo) {
        try {
            return await factsClient.post('/assessments', {
                    from_eth_address: ethAddress,
                    assessed_article: assessedArticle,
                    assessment_info: assessment
                },
                {
                    headers: {
                        "Content-type": "application/json",
                        "Authorization": `Bearer ${accessToken}`,
                    }
                }
            )
        } catch (error: any) {
            throw new Error(error.response?.data?.detail ?? "Error while creating assessment transaction", {cause: error})
        }
    },

    async confirmAssessmentTransaction(accessToken: string, assessmentId: string, signedTransaction: {}) {
        try {
            return await factsClient.post(`/assessments/${assessmentId}/signed`, signedTransaction,
                {
                    headers: {
                        "Content-type": "application/json",
                        "Authorization": `Bearer ${accessToken}`,
                    }
                }
            )
        }catch(error: any){
            throw new Error(error.response?.data?.detail ?? "Error while confirming assessment transaction", {cause: error})
        }
    },

}