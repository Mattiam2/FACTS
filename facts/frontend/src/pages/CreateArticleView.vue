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
                          v-model="articleUrl"
                          hide-details/>
              <VTextField label="Article Title" variant="outlined" prepend-inner-icon="mdi-format-title"
                          v-model="articleTitle"
                          hide-details/>
              <VTextField label="Article Author(s)" variant="outlined"
                          v-model="articleAuthor"
                          prepend-inner-icon="mdi-account-edit" hide-details/>
              <VTextarea label="Description" variant="outlined" prepend-inner-icon="mdi-text"
                         v-model="articleDescription"
                         hide-details/>
              <VDateInput
                  label="Publication Date"
                  prepend-icon=""
                  prepend-inner-icon="mdi-calendar"
                  variant="outlined"
                  v-model="articlePublicationDate"
                  hide-details
              />
              <VSelect
                  label="Language"
                  prepend-inner-icon="mdi-translate"
                  variant="outlined"
                  v-model="articleLanguage"
                  :items="['BG', 'CS', 'DA', 'DE', 'EL', 'EN', 'ES', 'ET', 'FI', 'FR', 'GA', 'HR', 'HU', 'IT', 'LT', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SL', 'SV']"
              />
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
        persistent
    >
      <VCard
          max-width="400"
          prepend-icon="mdi-update"
      >
        <VCardText>
          ETH Address: {{ appStore.ethWalletAddress }}
          <VTextField label="ETH Private Key" placeholder="0x..." type="password" class="ma-2" v-model="ethPrivateKey"
                      hide-details/>
          <VIcon icon="mdi-lock-outline" size="12"/>
          Your private key never leaves this device.
        </VCardText>
        <VCardActions>
          <VBtn
              class="ms-auto"
              text="Sign transaction"
              @click="signTransaction"
          />
        </VCardActions>
      </VCard>
    </VDialog>
  </VContainer>
</template>

<script lang="ts" setup>
import type {ArticleInfo} from "@/types";
import {ref} from "vue";
import {type Transaction, Web3} from "web3";
import AppLayout from "@/layouts/AppLayout.vue";
import {useAppStore} from "@/stores/app.ts";

const appStore = useAppStore()
const ethPrivateKey = ref('')
const transactionSignatureDialog = ref(false)

const transactionToSign = ref({})
const transactionDocumentHash = ref('')

const articleUrl = ref('')
const articleTitle = ref('')
const articleAuthor = ref('')
const articleDescription = ref('')
const articlePublicationDate = ref('')
const articleLanguage = ref('')

async function requestArticleCreation() {
  const article: ArticleInfo = {
    url: articleUrl.value,
    title: articleTitle.value,
    author: articleAuthor.value,
    description: articleDescription.value,
    publication_date: articlePublicationDate.value,
    language: articleLanguage.value,
    sources: []
  }
  const response = await appStore.createArticleTransaction(article)
  appStore.addToastMessage(`Received transaction`, 'success')
  console.log(response)
  transactionToSign.value = response.transaction
  transactionDocumentHash.value = response.document_hash
  transactionSignatureDialog.value = true
}

async function signTransaction() {
  if (!transactionDocumentHash.value || !transactionToSign.value) {
    appStore.addToastMessage(`No transaction to sign`, 'error')
    return
  }
  if (!ethPrivateKey.value) {
    appStore.addToastMessage(`Please enter your private key`, 'error')
    transactionSignatureDialog.value = true
    return
  }
  const web3 = new Web3()
  transactionSignatureDialog.value = false
  const transaction: Transaction = transactionToSign.value as Transaction
  transaction.gas = 103972
  const privateKey = ethPrivateKey.value
  const signedTx = await web3.eth.accounts.signTransaction(transaction, privateKey);
  const factsSignedTransaction = {
    protocol: "eth",
    unsignedTransaction: transaction,
    r: signedTx.r,
    s: signedTx.s,
    v: Number.parseInt(signedTx.v),
    signedRawTransaction: signedTx.rawTransaction.slice(2),
  }
  const response = await appStore.confirmArticleTransaction(transactionDocumentHash.value, factsSignedTransaction)
  if (response) {
    appStore.addToastMessage(`Article created`, 'success')
  }
}
</script>