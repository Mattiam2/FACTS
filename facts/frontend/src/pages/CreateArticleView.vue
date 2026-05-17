<template>
  <VContainer>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard>
          <VCardItem>
            <VCardTitle>Claim an Article</VCardTitle>
            <VCardSubtitle>Publish an article to FACTS.</VCardSubtitle>
          </VCardItem>
          <VCardText>
            <div class="d-flex flex-column ga-3">
              <VTextField label="Canonical URL" variant="outlined" prepend-inner-icon="mdi-link"
                          v-model="article.url"
                          hide-details/>
              <VTextField label="Article Title" variant="outlined" prepend-inner-icon="mdi-format-title"
                          v-model="article.title"
                          hide-details/>
              <VTextField label="Article Author(s)" variant="outlined"
                          v-model="article.author"
                          prepend-inner-icon="mdi-account-edit" hide-details/>
              <VTextarea label="Description" variant="outlined" prepend-inner-icon="mdi-text"
                         v-model="article.description"
                         hide-details/>
              <VDateInput
                  label="Publication Date"
                  prepend-icon=""
                  prepend-inner-icon="mdi-calendar"
                  variant="outlined"
                  v-model="article.publication_date"
                  autocomplete="off"
                  hide-details
              />
              <VSelect
                  label="Language"
                  prepend-inner-icon="mdi-translate"
                  variant="outlined"
                  v-model="article.language"
                  :items="['BG', 'CS', 'DA', 'DE', 'EL', 'EN', 'ES', 'ET', 'FI', 'FR', 'GA', 'HR', 'HU', 'IT', 'LT', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SL', 'SV']"
              />
              <VCard title="Sources" variant="tonal" class="mb-5">
                <VCardText>
                  <div v-for="(item, index) in article.sources" :key="index" class="d-flex align-center my-5">
                    <VTextField
                        v-model="article.sources[index]"
                        :label="'Source ' + (index + 1)"
                        density="compact"
                        variant="outlined"
                        hide-details
                        max-width="800"
                        class="mr-2"
                        placeholder="URL or Text"
                    />
                    <VBtn icon="mdi-delete" @click="article.sources.splice(index, 1)"
                          v-if="article.sources.length > 1" color="bg-red" class="me-2" density="compact"/>
                  </div>
                  <VBtn prepend-icon="mdi-plus" @click="article.sources.push('')" color="secondary">Add source</VBtn>
                </VCardText>
              </VCard>
            </div>
            <VBtn color="primary" @click="requestArticleCreation">Request</VBtn>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
    <VDialog
        v-model="transactionSignatureDialog"
        width="auto"
        title="You are signing the transaction"
    >
      <VCard
          max-width="400"
          prepend-icon="mdi-update"
          v-if="transactionToSign"
      >
        <VCardText>
          <VIcon>mdi-wallet</VIcon>
          {{ walletStore.ethWallet.ethAddress }}
          <div>
            Signing transaction:<br>
            <VTextarea readonly :model-value="JSON.stringify(transactionToSign)" class="my-2"/>
          </div>
        </VCardText>
        <VCardActions>
          <VBtn
              class="ms-auto"
              text="Sign transaction"
              @click="signTransaction"
          />
        </VCardActions>
      </VCard>
      <VCard
          max-width="400"
          prepend-icon="mdi-update"
          v-else
      >
        <VCardText>
          <VProgressCircular indeterminate/>
          Building transaction...
        </VCardText>
      </VCard>
    </VDialog>
  </VContainer>
</template>

<script lang="ts" setup>
import type {ArticleInfo} from "@/types";
import {type Ref, ref} from "vue";
import {type Transaction} from "web3";
import {useAppStore} from "@/stores/app.ts";
import {useArticleStore} from "@/stores/article.ts";
import {useAuthStore} from "@/stores/auth.ts";
import {useWalletStore} from "@/stores/wallet.ts";
import {sleep} from "@/utility.ts";

const appStore = useAppStore()
const authStore = useAuthStore()
const articleStore = useArticleStore()
const walletStore = useWalletStore()

const transactionSignatureDialog = ref(false)

const transactionToSign = ref({})
const transactionDocumentHash = ref('')

const article = ref({
  url: undefined,
  title: undefined,
  author: undefined,
  description: undefined,
  publication_date: undefined,
  language: undefined,
  sources: ['']
}) as Ref<ArticleInfo>

async function requestArticleCreation() {
  if(!authStore.factsAccessToken){
    appStore.addToastMessage(`Please login to FACTS`, 'error')
    return
  }
  if (!walletStore.ethWallet.ethAddress || !walletStore.ethWallet.privateKey) {
    appStore.addToastMessage(`Please link your wallet to FACTS`, 'error')
    return
  }
  transactionToSign.value = undefined
  transactionSignatureDialog.value = true
  article.value.sources = article.value.sources.filter(source => source.trim() !== '')
  const response = await articleStore.createArticleTransaction(authStore.factsAccessToken, walletStore.ethWallet.ethAddress, article.value)
  await sleep(1000)
  console.log(response)
  transactionToSign.value = response.transaction
  transactionDocumentHash.value = response.document_hash
}

async function signTransaction() {
  if(!authStore.factsAccessToken){
    appStore.addToastMessage(`Please login to FACTS`, 'error')
    return
  }
  if (!transactionDocumentHash.value || !transactionToSign.value) {
    appStore.addToastMessage(`No transaction to sign`, 'error')
    return
  }
  if (!walletStore.ethWallet.ethAddress || !walletStore.ethWallet.privateKey) {
    appStore.addToastMessage(`Please link your wallet to FACTS`, 'error')
    transactionSignatureDialog.value = true
    return
  }

  transactionSignatureDialog.value = false

  const transaction: Transaction = transactionToSign.value as Transaction
  transaction.gas = 103972
  const factsSignedTransaction = await walletStore.signTransaction(transaction)

  const response = await articleStore.confirmArticleTransaction(authStore.factsAccessToken, transactionDocumentHash.value, factsSignedTransaction)
  if (response) {
    appStore.addToastMessage(`Article created`, 'success')
  }
}
</script>