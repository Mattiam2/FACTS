import type {ArticleInfo} from "@/types";
import factsClient from '@/repositories/facts_base.ts'

export default {
    async getArticle(articleId: string) {
        try {
            return await factsClient.get(`/articles/${articleId}`)
        } catch (error: any) {
            if(error.response?.status == 404){
                return undefined
            }
            throw new Error(error.response?.data?.detail ?? "Error while fetching article", {cause: error})
        }
    },

    async getArticleSources(articleId: string) {
        try {
            return await factsClient.get(`/articles/${articleId}/sources`)
        } catch (error: any) {
            if(error.response?.status == 404){
                return undefined
            }
            throw new Error(error.response?.data?.detail ?? "Error while fetching article sources", {cause: error})
        }
    },

    async getArticles() {
        try {
            return await factsClient.get(`/articles`)
        } catch (error: any) {
            if(error.response?.status == 404){
                return undefined
            }
            throw new Error(error.response?.data?.detail ?? "Error while fetching articles", {cause: error})
        }
    },

    async getArticleByUrl(articleUrl: string) {
        try {
            return await factsClient.get(`/articles/by-url`, {
                params: {
                    url: articleUrl
                }
            })
        } catch (error: any) {
            if(error.response?.status == 404){
                return undefined
            }
            throw new Error(error.response?.data?.detail ?? "Error while fetching article", {cause: error})
        }
    },

    async createArticleTransaction(accessToken: string, ethAddress: string, articleInfo: ArticleInfo) {
        try {
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
        } catch (error: any) {
            throw new Error(error.response?.data?.detail ?? "Error while creating article transaction", {cause: error})
        }
    },

    async confirmArticleTransaction(accessToken: string, articleId: string, signedTransaction: {}) {
        try {
            return await factsClient.post(`/articles/${articleId}/signed`, signedTransaction,
                {
                    headers: {
                        "Content-type": "application/json",
                        "Authorization": `Bearer ${accessToken}`,
                    }
                }
            )
        } catch (error: any) {
            throw new Error(error.response?.data?.detail ?? "Error while confirming article transaction", {cause: error})
        }
    }

}