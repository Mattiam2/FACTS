import type {ArticleInfo, FactsSubjectCredential} from "@/types";
import { defineStore } from 'pinia'
import AuthRepo from '@/repositories/facts_auth.ts'

export const useAppStore = defineStore('app', {
  state: () => ({
    vcToken: undefined as string | undefined,
    factsCredentialSubject: undefined as FactsSubjectCredential | undefined,
    ethWallet: undefined as { eth_address: string, eth_private_key: string } | undefined,
    factsAccessToken: undefined as string | undefined,
    toastMessages: [] as {text: string, color?: string, onDismiss?: () => void}[],
  }),
  actions: {
    addToastMessage(text: string, type: 'success' | 'error' = 'success'){
      this.toastMessages.push({text, color: type})
    },
    async requestAccessToken(vpToken: string, scope: string){
      const response = await AuthRepo.authenticate(vpToken, scope)
      this.factsAccessToken = response.data.access_token
    },
    async createArticleTransaction(articleInfo: ArticleInfo){
      if(!this.factsAccessToken) {return}
      if(!this.ethWallet) {return}
      const response = await AuthRepo.create_article_transaction(this.factsAccessToken, this.ethWallet?.eth_address, articleInfo)
      console.log(response)
    }
  }
})
