import type {ArticleInfo, EbsiArticleDocument, IndexedArticle, SourceNode} from "@/types";
import {defineStore} from 'pinia'
import FactsArticleRepo from '@/repositories/facts_article.ts'

export const useArticleStore = defineStore('article', {
    state: () => ({
        articles: [] as IndexedArticle[],
        article: undefined as EbsiArticleDocument | undefined,
        article_sources: [] as SourceNode[],
    }),
    actions: {
        async getArticleByUrl(articleUrl: string): Promise<EbsiArticleDocument> {
            const response = await FactsArticleRepo.getArticleByUrl(articleUrl)
            return response?.data
        },
        async loadArticleByUrl(articleUrl: string) {
            const response = await FactsArticleRepo.getArticleByUrl(articleUrl)
            if(!response?.data) {
                return
            }
            this.article = response?.data
        },
        async loadArticle(articleId: string) {
            const response = await FactsArticleRepo.getArticle(articleId)
            if(!response?.data) {
                return
            }
            this.article = response?.data
        },
        async loadArticleSources(articleId: string) {
            const response = await FactsArticleRepo.getArticleSources(articleId)
            if(!response?.data || !response?.data.nodes || response?.data.nodes.length === 0) {
                return
            }
            const seen = new Set<string>()
            this.article_sources = response?.data.nodes.filter((node: SourceNode) => {
                if (!node.source_hash) {
                    return false
                }
                if (seen.has(node.source_hash)) {
                    return false
                }
                seen.add(node.source_hash)
                return true
            })
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
    persist: false,
})
