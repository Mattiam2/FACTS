<template>
  <VContainer fluid>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard variant="tonal">
          <VCardItem>
            <VCardTitle>Fact-checking Assessment Submission</VCardTitle>
            <VCardSubtitle>Insert information about the article you are evaluating.</VCardSubtitle>
          </VCardItem>
          <VCardText>
            <VForm v-if="submissionStep == 1" ref="formURL">
              <div class="d-flex ga-2">
                <VTextField label="Canonical URL" variant="outlined" prepend-inner-icon="mdi-link"
                            v-model="articleUrl"
                            :rules="[rules.url, rules.required]"
                            density="compact">
                  <template #details>
                    <span v-if="articleFoundOnEBSI === true" class="text-cyan-accent-2"><VIcon>mdi-check-circle</VIcon> Found on EBSI</span>
                    <span v-else-if="articleFoundOnEBSI === false" class="text-amber-darken-2"><VIcon>mdi-close-circle</VIcon> Not Found on EBSI</span>
                  </template>
                </VTextField>
                <VBtn color="primary" @click="checkArticle" :disabled="!formURL?.isValid">Check</VBtn>
              </div>
            </VForm>
            <VForm v-if="submissionStep == 1" ref="formStep1">
              <div class="d-flex flex-column ga-3 mt-10" v-if="articleFoundOnEBSI !== undefined">
                <VCard class="mb-5" v-if="claimedByPublisher" title="Publisher" variant="tonal">
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
                    input-format="dd/mm/yyyy"
                    :rules="[rules.required]"
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
                <VBtn color="primary" @click="submissionStep++" :disabled="!formStep1?.isValid">Next</VBtn>
              </div>
            </VForm>
            <VForm v-if="submissionStep == 2" ref="formStep2">
              <div class="d-flex flex-column ga-3 mt-10">
                <VDateInput label="Assessment Date" variant="outlined"
                            prepend-icon=""
                            prepend-inner-icon="mdi-calendar"
                            v-model="assessmentInfo.assessment_date"
                            autocomplete="off"
                            input-format="dd/mm/yyyy"
                            :rules="[rules.required]"
                            hide-details/>
                <VDivider/>
                Credibility score:
                <div class="d-flex">
                  <VRating
                      v-model="assessmentInfo.credibility_evaluation.score"
                      hover
                      :length="5"
                      :size="32"
                      active-color="primary"
                      :rules="[rules.required]"
                      class="mr-5"
                  />
                  <span v-if="assessmentInfo.credibility_evaluation.score" class="text-title-medium"
                        style="line-height: 32px">{{
                      getCredibilityDescription(assessmentInfo.credibility_evaluation.score)
                    }}</span>
                </div>
                <VTextarea label="Credibility Note" variant="outlined"
                           v-model="assessmentInfo.credibility_evaluation.note"
                           prepend-inner-icon="mdi-account-edit" :rules="[rules.required]" hide-details/>
                <VDivider/>
                Manipulation score:
                <div class="d-flex">
                  <VRating
                      v-model="assessmentInfo.manipulation_evaluation.score"
                      hover
                      :length="5"
                      :size="32"
                      active-color="primary"
                      :rules="[rules.required]"
                      class="mr-5"
                  />
                  <span v-if="assessmentInfo.manipulation_evaluation.score" class="text-title-medium"
                        style="line-height: 32px">{{
                      getManipulationDescription(assessmentInfo.manipulation_evaluation.score)
                    }}</span>
                </div>
                <VTextarea label="Manipulation Note" variant="outlined"
                           v-model="assessmentInfo.manipulation_evaluation.note"
                           prepend-inner-icon="mdi-account-edit" :rules="[rules.required]"
                           hide-details/>
                <VBtn color="secondary" @click="submissionStep--">Back</VBtn>
                <VBtn color="primary" @click="requestAssessmentCreation" :disabled="!formStep2?.isValid">Submit
                  Assessment
                </VBtn>
              </div>
            </VForm>
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
import router from "@/router";
import {useAppStore} from "@/stores/app.ts";
import {useArticleStore} from "@/stores/article.ts";
import {useAssessmentStore} from "@/stores/assessment.ts";
import {useAuthStore} from "@/stores/auth.ts";
import {useWalletStore} from "@/stores/wallet.ts";
import {
  extractSubjectCredential,
  getCredibilityDescription,
  getManipulationDescription,
  rules,
  sleep
} from "@/utility.ts";

const appStore = useAppStore()
const articleStore = useArticleStore()
const authStore = useAuthStore()
const walletStore = useWalletStore()
const assessmentStore = useAssessmentStore()

const formStep1 = ref(null) as Ref<any>
const formStep2 = ref(null) as Ref<any>
const formURL = ref(null) as Ref<any>

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
  assessment_date: new Date().toISOString().split('T')[0],
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
  let response = undefined
  try {
    response = await assessmentStore.createAssessmentTransaction(authStore.factsAccessToken, walletStore.ethWallet.ethAddress, assessedArticle.value, assessmentInfo.value)
  } catch (error: any) {
    console.log(error)
    appStore.addToastMessage(`Error creating assessment transaction: ${error.message}`, 'error')
    transactionSignatureDialog.value = false
    return
  }
  await sleep(1000)
  console.log(response)
  transactionToSign.value = response.transaction
  transactionDocumentHash.value = response.document_hash
}

async function checkArticle() {
  try {
    await articleStore.loadArticleByUrl(articleUrl.value)
  } catch (error: any) {
    console.log(error)
    appStore.addToastMessage(`Error loading article: ${error.message}`, 'error')
    return
  }
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
    return
  }
  transactionSignatureDialog.value = false
  const transaction: Transaction = transactionToSign.value as Transaction
  transaction.gas = 999999
  let factsSignedTransaction = undefined
  try {
    factsSignedTransaction = await walletStore.signTransaction(transaction)
  } catch (error: any) {
    console.log(error)
    appStore.addToastMessage(`Error signing transaction: ${error.message}`, 'error')
    return
  }

  let response = undefined
  try {
    response = await assessmentStore.confirmAssessmentTransaction(authStore.factsAccessToken, transactionDocumentHash.value, factsSignedTransaction)
  } catch (error: any) {
    console.error(error)
    appStore.addToastMessage(`Error confirming assessment transaction: ${error.message}`, 'error')
    return
  }
  if (response) {
    appStore.addToastMessage(`Assessment created`, 'success')
    await router.push({path: '/assessments'})
  }
}

onMounted(() => {
  submissionStep.value = 1;
})
</script>