<template>
  <VContainer>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard variant="tonal">
          <VCardItem>
            <VCardTitle>Assessment list</VCardTitle>
          </VCardItem>
          <VCardText>
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

const assessmentStore = useAssessmentStore()

const {assessments} = storeToRefs(assessmentStore)

const assessmentHeaders = [
  {title: 'Assess. ID', key: 'hash', value: (assessment: any) => assessment.hash.slice(0, 10) + '...'},
  {title: 'Date', key: 'timestamp'},
  {title: 'Url', key: 'article_url'},
  {title: 'Credibility Score', key: 'credibility_score'},
  {title: 'Manipulation Score', key: 'manipulation_score'},
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