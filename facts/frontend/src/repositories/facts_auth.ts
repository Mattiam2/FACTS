import type {ArticleInfo, AssessedArticleInfo, AssessmentInfo} from "@/types";
import factsClient from '@/repositories/facts_base.ts'

export default {

    async authenticate(vpToken: string, scope: string) {
        return await factsClient.post('/auth/token', {
            "vp_token": vpToken,
            scope,
        })
    },

    async createArticleTransaction(accessToken: string, ethAddress: string, articleInfo: ArticleInfo) {
        return await factsClient.post('/articles', {
                from_eth_address: ethAddress,
                article_info: articleInfo
            },
            {
                headers: {
                    "Content-type": "application/json",
                    "Authorization": `Bearer ${accessToken}`,
                }
            }
        )
    },

    async confirmArticleTransaction(accessToken: string, articleId: string, signedTransaction: {}) {
        return await factsClient.post(`/articles/${articleId}/signed`, signedTransaction,
            {
                headers: {
                    "Content-type": "application/json",
                    "Authorization": `Bearer ${accessToken}`,
                }
            }
        )
    },

    async getArticle(articleId: string) {
        let response = undefined
        try {
            response = await factsClient.get(`/articles/${articleId}`)
        }catch(error){
            console.log(error)
        }
        return response
    },

    async getArticles() {
        let response = undefined
        try {
            response = await factsClient.get(`/articles`)
        }catch(error){
            console.log(error)
        }
        return response
    },

    async getArticleByUrl(articleUrl: string) {
        let response = undefined
        try {
            response = await factsClient.get(`/articles/by-url`, {
                params: {
                    url: articleUrl
                }
            })
        }catch(error){
            console.log(error)
        }
        return response
    },
    async getAssessment(assessmentId: string){
        return await factsClient.get(`/assessments/${assessmentId}`)
    },
    async getAssessments(articleId: string){
        return await factsClient.get('/assessments', {
            params: {
                article_hash: articleId
            }
        })
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