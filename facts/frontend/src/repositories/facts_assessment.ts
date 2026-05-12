import type {AssessedArticleInfo, AssessmentInfo} from "@/types";
import factsClient from '@/repositories/facts_base.ts'

export default {

    async getAssessment(assessmentId: string){
        return await factsClient.get(`/assessments/${assessmentId}`)
    },
    async getAssessments(articleId?: string){
        let params = {}
        if(articleId){
            params = {
                article_hash: articleId
            }
        }
        return await factsClient.get('/assessments', {params})
    },

    async createAssessmentTransaction(accessToken: string, ethAddress: string, assessedArticle: AssessedArticleInfo, assessment: AssessmentInfo) {
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
    },

    async confirmAssessmentTransaction(accessToken: string, assessmentId: string, signedTransaction: {}) {
        return await factsClient.post(`/assessments/${assessmentId}/signed`, signedTransaction,
            {
                headers: {
                    "Content-type": "application/json",
                    "Authorization": `Bearer ${accessToken}`,
                }
            }
        )
    },

}