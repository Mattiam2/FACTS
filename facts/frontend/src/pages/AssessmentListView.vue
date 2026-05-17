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
import {useAssessmentStore} from "@/stores/assessment.ts";
import {useAuthStore} from "@/stores/auth.ts";
import {formatDate} from "@/utility.ts";

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

function openArticleWebsite(assessment: IndexedAssessment) {
  window.open(assessment.article_url, '_blank')
}

function openArticleClaim(assessment: IndexedAssessment) {
  router.push(`/articles/${assessment.article_hash}`)
}

onMounted(async () => {
  await assessmentStore.loadAssessments()
})
</script>