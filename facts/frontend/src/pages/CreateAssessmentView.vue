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
                    autocomplete="off"
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
                            autocomplete="off"
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
    >
      <VCard
          max-width="500"
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
              text="Sign transaction"
              @click="signTransaction"
              color="primary"
              variant="elevated"
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
import type {AssessedArticleInfo, AssessmentInfo, FactsSubjectCredential} from "@/types";
import type {Transaction} from "web3";
import {onMounted, type Ref, ref} from "vue";
import {useAppStore} from "@/stores/app.ts";
import {useArticleStore} from "@/stores/article.ts";
import {useAssessmentStore} from "@/stores/assessment.ts";
import {useAuthStore} from "@/stores/auth.ts";
import {useWalletStore} from "@/stores/wallet.ts";
import {extractSubjectCredential, sleep} from "@/utility.ts";

const appStore = useAppStore()
const articleStore = useArticleStore()
const authStore = useAuthStore()
const walletStore = useWalletStore()
const assessmentStore = useAssessmentStore()

const transactionSignatureDialog = ref(false)

const transactionToSign = ref(undefined) as Ref<object | undefined>
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
  if (!authStore.factsAccessToken) {
    appStore.addToastMessage(`Please login to FACTS`, 'error')
    return
  }
  if (!walletStore.ethWallet.ethAddress || !walletStore.ethWallet.privateKey) {
    appStore.addToastMessage(`Please link your wallet to FACTS`, 'error')
    return
  }
  transactionToSign.value = undefined
  transactionSignatureDialog.value = true
  const response = await assessmentStore.createAssessmentTransaction(authStore.factsAccessToken, walletStore.ethWallet.ethAddress, assessedArticle.value, assessmentInfo.value)
  await sleep(1000)
  console.log(response)
  transactionToSign.value = response.transaction
  transactionDocumentHash.value = response.document_hash
}

async function checkArticle() {
  await articleStore.loadArticleByUrl(articleUrl.value)
  assessmentInfo.value.article_url = articleUrl.value
  if (articleStore.article) {
    claimedByPublisher.value = extractSubjectCredential(articleStore.article.metadata.publisher_vc)
    articleUrl.value = articleStore.article.metadata.article_info.url ?? articleUrl.value
    assessedArticle.value.title = articleStore.article.metadata.article_info.title
    assessedArticle.value.author = articleStore.article.metadata.article_info.author
    assessedArticle.value.description = articleStore.article.metadata.article_info.description
    assessedArticle.value.publication_date = articleStore.article.metadata.article_info.publication_date
    assessedArticle.value.language = articleStore.article.metadata.article_info.language
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
  if (!authStore.factsAccessToken) {
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

  const response = await assessmentStore.confirmAssessmentTransaction(authStore.factsAccessToken, transactionDocumentHash.value, factsSignedTransaction)
  if (response) {
    appStore.addToastMessage(`Assessment created`, 'success')
  }
}

onMounted(() => {
  submissionStep.value = 1;
})
</script>