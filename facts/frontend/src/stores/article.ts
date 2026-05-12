import type {ArticleInfo, EbsiArticleDocument, IndexedArticle} from "@/types";
import {defineStore} from 'pinia'
import FactsArticleRepo from '@/repositories/facts_article.ts'

export const useArticleStore = defineStore('article', {
    state: () => ({
        articles: [] as IndexedArticle[],
        article: undefined as EbsiArticleDocument | undefined,
    }),
    actions: {
        async getArticleByUrl(articleUrl: string): Promise<EbsiArticleDocument> {
            const response = await FactsArticleRepo.getArticleByUrl(articleUrl)
            return response?.data
        },
        async loadArticleByUrl(articleUrl: string) {
            const response = await FactsArticleRepo.getArticleByUrl(articleUrl)
            this.article = response?.data
        },
        async loadArticle(articleId: string) {
            const response = await FactsArticleRepo.getArticle(articleId)
            this.article = response?.data
        },
        async loadArticles() {
            const response = await FactsArticleRepo.getArticles()
            this.articles = response?.data
        },
        async createArticleTransaction(factsAccessToken: string, ethAddress: string, articleInfo: ArticleInfo) {
            if (!factsAccessToken) {
                return
            }
            if (!ethAddress) {
                return
            }
            const response = await FactsArticleRepo.createArticleTransaction(factsAccessToken, ethAddress, articleInfo)
            return response?.data
        },
        async confirmArticleTransaction(factsAccessToken: string, articleId: string, signedTransaction: {}) {
            if (!factsAccessToken) {
                return
            }
            const response = await FactsArticleRepo.confirmArticleTransaction(factsAccessToken, articleId, signedTransaction)
            return response?.data
        }
    },
    persist: true,
})
