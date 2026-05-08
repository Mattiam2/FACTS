import type {ArticleInfo} from "@/types";
import factsClient from '@/repositories/facts_base.ts'

export default {
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
    }

}