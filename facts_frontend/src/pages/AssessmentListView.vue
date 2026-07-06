<template>
  <VContainer fluid>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard variant="tonal">
          <VCardItem>
            <VCardTitle>Assessment list</VCardTitle>
          </VCardItem>
          <VCardText>
            <VBtn color="primary" class="top-0 mt-4 mr-3 right-0 position-absolute" :to="{path: '/assessments/submit'}" v-if="authStore.factsCredentialSubject?.role == 'factChecker'">
              Submit a new assessment
            </VBtn>

            <VDataTable :items="assessments" :headers="assessmentHeaders" class="bg-transparent">
              <template #item.actions="{ item }">
                <div class="d-flex ga-2">
                  <VBtn
                      @click.stop="openArticleWebsite(item)"
                      color="primary"
                  >Open URL
                  </VBtn>
                  <VBtn
                      @click.stop="openArticleClaim(item)"
                      color="primary"
                  >See Article Claim
                  </VBtn>
                </div>
              </template>
              <template #item.credibility_score="{ item }">
                <VProgressLinear :model-value="(item.credibility_score / 5)*100" :color="item.credibility_score > 3 ? 'success' : item.credibility_score > 1 ? 'warning' : 'error'" height="10" rounded/>
              </template>
              <template #item.manipulation_score="{ item }">
                <VProgressLinear :model-value="(item.manipulation_score / 5)*100" :color="item.manipulation_score > 3 ? 'success' : item.manipulation_score > 1 ? 'warning' : 'error'" height="10" rounded/>
              </template>
              <template #item.timestamp="{ value }">
                {{ formatDate(value) }}
              </template>
            </VDataTable>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>

  </VContainer>
</template>

<script lang="ts" setup>
import type {IndexedAssessment} from "@/types";
import {storeToRefs} from "pinia";
import {onMounted} from "vue";
import router from "@/router";
import {useAppStore} from "@/stores/app.ts";
import {useAssessmentStore} from "@/stores/assessment.ts";
import {useAuthStore} from "@/stores/auth.ts";
import {formatDate} from "@/utility.ts";

const appStore = useAppStore()
const assessmentStore = useAssessmentStore()
const authStore = useAuthStore()

const {assessments} = storeToRefs(assessmentStore)

const assessmentHeaders = [
  {title: 'Assess. ID', key: 'hash', value: (assessment: any) => assessment.hash.slice(0, 10) + '...'},
  {title: 'Date', key: 'timestamp'},
  {title: 'Url', key: 'article_url'},
  {title: 'Cred.', key: 'credibility_score'},
  {title: 'Manip.', key: 'manipulation_score'},
  {title: 'DID Creator', key: 'creator'},
  {title: '', key: 'actions'},
]

/**
 * Opens the article website in a new browser tab based on the given assessment object.
 *
 * @param {IndexedAssessment} assessment - The assessment object containing the URL of the article to be opened.
 * @return {void} Does not return a value.
 */
function openArticleWebsite(assessment: IndexedAssessment) {
  window.open(assessment.article_url, '_blank')
}

/**
 * Navigates to the claim page of the specified article by utilizing its unique hash.
 *
 * @param {IndexedAssessment} assessment - An object containing information about the assessment, including the article's unique hash.
 * @return {void} Does not return any value.
 */
function openArticleClaim(assessment: IndexedAssessment) {
  router.push(`/articles/${assessment.article_hash}`)
}

/**
 * Loads assessments by retrieving them from the assessment store.
 * If an error occurs during the process, logs the error.
 *
 * @return {Promise<void>} A promise that resolves when the assessments are successfully loaded.
 */
async function loadAssessments() {
  try {
    await assessmentStore.loadAssessments()
  } catch (error: any) {
    console.error(error)
    appStore.addToastMessage(`Error loading assessments: ${error.message}`, 'error')
  }
}

onMounted(async () => {
  await loadAssessments()
})
</script>