<template>
  <VContainer>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard>
          <VCardItem>
            <VCardTitle>Article Claim - HASH: {{ route.params.id }}</VCardTitle>
          </VCardItem>
          <VCardText>
            <VCard class="mb-5" v-if="claimedByPublisher" title="Publisher" variant="tonal">
              <VCardText>
                <b>DID</b>: {{ claimedByPublisher.id }}<br>
                <b>Company</b>: {{ claimedByPublisher.company_name }}<br>
                <b>Website</b>: <a :href="claimedByPublisher.company_website"
                                   target="_blank">{{ claimedByPublisher.company_website }}</a>
              </VCardText>
            </VCard>
            <VCard v-if="article" variant="tonal" title="Article">
              <VCardText>
                <b>Title</b>: {{ article.metadata.article_info.title }}<br/>
                <b>Author</b>: {{ article.metadata.article_info.author }}<br/>
                <b>Description</b>: {{ article.metadata.article_info.description }}<br/>
                <b>Publication Date</b>: {{ article.metadata.article_info.publication_date }}<br/>
                <b>Language</b>: {{ article.metadata.article_info.language }}<br/>
                <div v-if="article.metadata.article_info.sources && article.metadata.article_info.sources.length > 0">
                  <b>Sources</b>:
                  <div v-for="source in article.metadata.article_info.sources" :key="source" class="d-flex ga-2">
                    <VIcon icon="mdi-link" color="primary" size="16"/>
                    {{ source }}
                  </div>
                </div>

              </VCardText>
            </VCard>
            <VCard variant="tonal" v-else>
              <VCardText>No publisher claim for this article, only fact-checking assessments found.</VCardText>
            </VCard>
            <VCard v-if="assessments && assessments.length > 0" class="mt-5" title="Fact-checking assessments"
                   variant="tonal">
              <VCardText>
                <VContainer>
                  <VRow>
                    <VCol cols="6">
                      <VCard title="Average Credibility Score">
                        <VCardText class="d-flex justify-center">
                          <Gauge :value="averageCredibilityScore"/>
                        </VCardText>
                      </VCard>
                    </VCol>
                    <VCol cols="6">
                      <VCard title="Average Manipulation Score">
                        <VCardText class="d-flex justify-center">
                          <Gauge :value="averageManipulationScore"/>
                        </VCardText>
                      </VCard>
                    </VCol>
                  </VRow>
                </VContainer>


                <VDataTable :items="assessments" :headers="assessmentHeaders" show-expand hide-default-footer>
                  <template #item.data-table-expand="{ internalItem, isExpanded, toggleExpand, item }">
                    <VBtn
                        :append-icon="isExpanded(internalItem) ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                        :text="isExpanded(internalItem) ? 'Collapse' : 'More info'"
                        class="text-none"
                        color="medium-emphasis"
                        size="small"
                        variant="text"
                        width="105"
                        border
                        slim
                        @click="expandAssessment(item, toggleExpand)"
                    />
                  </template>
                  <template #expanded-row="{ columns, item }">
                    <tr>
                      <td :colspan="columns.length">
                        <VContainer>
                          <VRow>
                            <VCol cols="4">
                              <VCard class="mb-5" v-if="item.subjectCredential" title="Issued by">
                                <VCardText>
                                  <b>DID</b>: {{ item.subjectCredential.id }}<br>
                                  <b>Company</b>: {{ item.subjectCredential.company_name }}<br>
                                  <b>Website</b>: <a :href="item.subjectCredential.company_website"
                                                     target="_blank">{{ item.subjectCredential.company_website }}</a>
                                </VCardText>
                              </VCard>
                            </VCol>
                            <VCol cols="4" v-if="item.assessmentInfo?.credibility_evaluation">
                              <VCard title="Credibility Evaluation">
                                <VCardText class="d-flex flex-column align-center">
                                  <Gauge :value="item.assessmentInfo?.credibility_evaluation.score"/>
                                  <br>
                                  Note: {{ item.assessmentInfo?.credibility_evaluation.note }}<br>
                                </VCardText>
                              </VCard>
                            </VCol>
                            <VCol cols="4" v-if="item.assessmentInfo?.manipulation_evaluation">
                              <VCard title="Manipulation Evaluation">
                                <VCardText class="d-flex flex-column align-center">
                                  <Gauge :value="item.assessmentInfo?.manipulation_evaluation.score"/>
                                  <br>
                                  Note: {{ item.assessmentInfo?.manipulation_evaluation.note }}
                                </VCardText>
                              </VCard>
                            </VCol>
                          </VRow>
                          <VRow>
                            <VCol cols="12"
                                  v-if="item.assessmentInfo?.evidences && item.assessmentInfo?.evidences.length > 0">
                              Evidences:
                              <div v-for="evidence in item.assessmentInfo?.evidences" :key="evidence"
                                   class="d-flex ga-2">
                                <VIcon icon="mdi-link" color="primary" size="16"/>
                                {{ evidence }}
                              </div>
                            </VCol>
                          </VRow>
                        </VContainer>
                      </td>
                    </tr>
                  </template>
                </VDataTable>

              </VCardText>
            </VCard>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
  </VContainer>
</template>

<script lang="ts" setup>
import type {Assessment, EbsiArticleDocument, EbsiAssessmentDocument, FactsSubjectCredential} from "@/types";
import {onMounted, type Ref, ref} from "vue";
import {useRoute} from "vue-router";
import {useAppStore} from "@/stores/app.ts";
import Gauge from "@/components/Gauge.vue";

const route = useRoute()

const appStore = useAppStore()
const article = ref(undefined) as Ref<EbsiArticleDocument | undefined>
const claimedByPublisher = ref(undefined) as Ref<FactsSubjectCredential | undefined>
const assessments = ref([]) as Ref<Assessment[]>
const averageCredibilityScore = ref(0)
const averageManipulationScore = ref(0)

const assessmentHeaders = [
  {title: 'Assessment ID', key: 'hash', value: (assessment: any) => assessment.hash.slice(0, 10) + '...'},
  {title: 'Date', key: 'timestamp'},
  {title: 'Credibility Score', key: 'credibility_score'},
  {title: 'Manipulation Score', key: 'manipulation_score'},
  {title: 'DID Creator', key: 'creator'},
  {title: '', key: 'data-table-expand'},
]

async function expandAssessment(item: Assessment, expand: any) {
  const ebsi_document: EbsiAssessmentDocument = await appStore.getAssessment(item.hash)
  item.assessmentInfo = ebsi_document.metadata.assessment_info
  item.subjectCredential = appStore.extractSubjectCredential(ebsi_document.metadata.fact_checker_vc)
  expand(item)
}

onMounted(async () => {
  article.value = await appStore.getArticle(route.params.id as string)
  if (article.value)
    claimedByPublisher.value = appStore.extractSubjectCredential(article.value.metadata.publisher_vc)
  assessments.value = await appStore.getAssessments(route.params.id as string)
  let credibilityScoreSum = 0
  let credibilityScoreCount = 0
  let manipulationScoreSum = 0
  let manipulationScoreCount = 0
  for (const assessment of assessments.value) {
    if (assessment.credibility_score !== undefined) {
      credibilityScoreSum += assessment.credibility_score
      credibilityScoreCount++
    }
    if (assessment.manipulation_score !== undefined) {
      manipulationScoreSum += assessment.manipulation_score
      manipulationScoreCount++
    }
  }
  if (credibilityScoreCount > 0) {
    averageCredibilityScore.value = credibilityScoreSum / credibilityScoreCount
  }
  if (manipulationScoreCount > 0) {
    averageManipulationScore.value = manipulationScoreSum / manipulationScoreCount
  }
})
</script>