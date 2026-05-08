<template>
  <VContainer>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard>
          <VCardItem>
            <VCardTitle>Fact-checking Assessment Submission</VCardTitle>
            <VCardSubtitle>Insert information about the article you are evaluating.</VCardSubtitle>
          </VCardItem>
          <VCardText>
            <div v-if="submissionStep == 1">
              <div class="d-flex ga-2">
                <VTextField label="Canonical URL" variant="outlined" prepend-inner-icon="mdi-link"
                            v-model="articleUrl"
                            density="compact">
                  <template #details>
                    <span v-if="articleFoundOnEBSI === true" class="text-cyan-accent-2"><VIcon>mdi-check-circle</VIcon> Found on EBSI</span>
                    <span v-else-if="articleFoundOnEBSI === false" class="text-amber-darken-2"><VIcon>mdi-close-circle</VIcon> Not Found on EBSI</span>
                  </template>
                </VTextField>
                <VBtn color="primary" @click="checkArticle">Check</VBtn>
              </div>
              <div class="d-flex flex-column ga-3 mt-10" v-if="articleFoundOnEBSI !== undefined">
                <VCard class="mb-5" v-if="claimedByPublisher" title="Publisher">
                  <VCardText>
                    <b>DID</b>: {{ claimedByPublisher.id }}<br>
                    <b>Company</b>: {{ claimedByPublisher.company_name }}<br>
                    <b>Website</b>: <a :href="claimedByPublisher.company_website"
                                       target="_blank">{{ claimedByPublisher.company_website }}</a>
                  </VCardText>
                </VCard>
                <span
                    v-if="!articleFoundOnEBSI">Article not present on EBSI, please complete with the article data:</span>
                <VTextField label="Article Title" variant="outlined" prepend-inner-icon="mdi-format-title"
                            v-model="assessedArticle.title"
                            :disabled="articleFoundOnEBSI"
                            hide-details/>
                <VTextField label="Article Author(s)" variant="outlined"
                            v-model="assessedArticle.author"
                            :disabled="articleFoundOnEBSI"
                            prepend-inner-icon="mdi-account-edit" hide-details/>
                <VTextarea label="Description" variant="outlined" prepend-inner-icon="mdi-text"
                           v-model="assessedArticle.description"
                           :disabled="articleFoundOnEBSI"
                           hide-details/>
                <VDateInput
                    label="Publication Date"
                    prepend-icon=""
                    prepend-inner-icon="mdi-calendar"
                    variant="outlined"
                    v-model="assessedArticle.publication_date"
                    :disabled="articleFoundOnEBSI"
                    hide-details
                />
                <VSelect
                    label="Language"
                    prepend-inner-icon="mdi-translate"
                    variant="outlined"
                    v-model="assessedArticle.language"
                    :disabled="articleFoundOnEBSI"
                    :items="['BG', 'CS', 'DA', 'DE', 'EL', 'EN', 'ES', 'ET', 'FI', 'FR', 'GA', 'HR', 'HU', 'IT', 'LT', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SL', 'SV']"
                />
                <VBtn color="primary" @click="submissionStep++">Next</VBtn>
              </div>
            </div>
            <div v-if="submissionStep == 2">
              <div class="d-flex flex-column ga-3 mt-10">
                <VDateInput label="Assessment Date" variant="outlined" prepend-inner-icon="mdi-format-title"
                            prepend-icon=""
                            v-model="assessmentInfo.assessment_date"
                            hide-details/>
                <VTextField label="Credibility Evaluation Note" variant="outlined"
                            v-model="assessmentInfo.credibility_evaluation.note"
                            prepend-inner-icon="mdi-account-edit" hide-details/>
                <VTextField label="Credibility Evaluation Score" variant="outlined"
                            v-model="assessmentInfo.credibility_evaluation.score"
                            prepend-inner-icon="mdi-account-edit" hide-details/>
                <VTextField label="Manipulation Evaluation Notes" variant="outlined"
                            v-model="assessmentInfo.manipulation_evaluation.note"
                            prepend-inner-icon="mdi-account-edit" hide-details/>
                <VTextField label="Manipulation Evaluation Score" variant="outlined"
                            v-model="assessmentInfo.manipulation_evaluation.score"
                            prepend-inner-icon="mdi-account-edit" hide-details/>
                <VBtn color="primary" @click="requestAssessmentCreation">Submit Assessment</VBtn>
              </div>
            </div>
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
import type {AssessedArticleInfo, AssessmentInfo, FactsSubjectCredential} from "@/types";
import {onMounted, type Ref, ref} from "vue";
import {type Transaction, Web3} from "web3";
import AppLayout from "@/layouts/AppLayout.vue";
import {useAppStore} from "@/stores/app.ts";

const appStore = useAppStore()
const ethPrivateKey = ref('')
const transactionSignatureDialog = ref(false)

const transactionToSign = ref({})
const transactionDocumentHash = ref('')

const submissionStep = ref(0)

const articleUrl = ref('')
const assessedArticle = ref({
  title: undefined,
  author: undefined,
  description: undefined,
  publication_date: undefined,
  language: undefined,
  sources: [],
}) as Ref<AssessedArticleInfo>

const assessmentInfo = ref({
  article_url: undefined,
  assessment_date: undefined,
  credibility_evaluation: {
    note: undefined,
    score: undefined,
  },
  manipulation_evaluation: {
    note: undefined,
    score: undefined,
  },
  evidences: []
}) as Ref<AssessmentInfo>

const claimedByPublisher = ref(undefined) as Ref<FactsSubjectCredential | undefined>

const articleFoundOnEBSI = ref(undefined) as Ref<boolean | undefined>

async function requestAssessmentCreation() {
  const response = await appStore.createAssessmentTransaction(assessedArticle.value, assessmentInfo.value)
  appStore.addToastMessage(`Received transaction`, 'success')
  console.log(response)
  transactionToSign.value = response.transaction
  transactionDocumentHash.value = response.document_hash
  transactionSignatureDialog.value = true
}

async function checkArticle() {
  const article = await appStore.getArticleByUrl(articleUrl.value)
  assessmentInfo.value.article_url = articleUrl.value
  if (article) {
    claimedByPublisher.value = appStore.extractSubjectCredential(article.publisher_vc)
    articleUrl.value = article.article_info.url
    assessedArticle.value.title = article.article_info.title
    assessedArticle.value.author = article.article_info.author
    assessedArticle.value.description = article.article_info.description
    assessedArticle.value.publication_date = article.article_info.publication_date
    assessedArticle.value.language = article.article_info.language
    articleFoundOnEBSI.value = true
  } else {
    claimedByPublisher.value = undefined
    assessedArticle.value.title = ""
    assessedArticle.value.author = ""
    assessedArticle.value.description = ""
    assessedArticle.value.publication_date = ""
    assessedArticle.value.language = ""
    articleFoundOnEBSI.value = false
  }
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
  const response = await appStore.confirmAssessmentTransaction(transactionDocumentHash.value, factsSignedTransaction)
  if (response) {
    appStore.addToastMessage(`Assessment created`, 'success')
  }
}

onMounted(() => {
  submissionStep.value = 1;
})
</script>