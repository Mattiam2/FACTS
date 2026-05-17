<template>
  <VContainer fluid>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard variant="tonal">
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
                <b>URL</b>: <a :href="article.metadata.article_info.url"
                               target="_blank">{{ article.metadata.article_info.url }}</a><br>
                <b>Title</b>: {{ article.metadata.article_info.title }}<br>
                <b>Author</b>: {{ article.metadata.article_info.author }}<br>
                <b>Description</b>: {{ article.metadata.article_info.description }}<br>
                <b>Publication Date</b>: {{ formatDate(article.metadata.article_info.publication_date) }}<br>
                <b>Language</b>: {{ article.metadata.article_info.language }}<br>
                <div v-if="article.metadata.article_info.sources && article.metadata.article_info.sources.length > 0">
                  <b>Sources</b>:
                  <div v-for="source in article.metadata.article_info.sources" :key="source" class="d-flex ga-2">
                    <a :href="source" target="_blank" v-if="source.startsWith('http')" class="text-decoration-none">
                      <VIcon icon="mdi-link" color="primary" size="16"/>
                      <span class="text-decoration-underline ms-1">{{ source }}</span>
                    </a>
                    <span v-else>{{ source }}</span>

                  </div>
                </div>

              </VCardText>
            </VCard>
            <VCard variant="tonal" v-else>
              <VCardText>
                <div v-if="assessments.length > 0 && assessments[0].article_url" class="mb-3">
                  <b>URL</b>: <a :href="assessments[0].article_url" target="_blank">{{ assessments[0].article_url }}</a>
                </div>
                <div v-if="assessments.length > 0">
                  <VIcon class="me-1">mdi-alert</VIcon>
                  No publisher claim for this article, only fact-checking assessments found.
                </div>
                <div v-else>
                  <VIcon class="me-1">mdi-alert</VIcon>
                  No publisher claim for this article and no fact-checking assessments found.
                </div>
              </VCardText>
            </VCard>
            <VCard v-if="assessments && assessments.length > 0" class="mt-5" title="Fact-checking assessments"
                   variant="tonal">
              <VCardText>
                <VContainer>
                  <VRow>
                    <VCol cols="6">
                      <VCard title="Average Credibility Score" variant="tonal" class="h-100">
                        <VCardText class="d-flex flex-column align-center">
                          <Gauge :value="averageCredibilityScore"/>
                          <h2>Probably {{ credibilityDescription }}</h2>
                        </VCardText>
                      </VCard>
                    </VCol>
                    <VCol cols="6">
                      <VCard title="Average Manipulation Score" variant="tonal" class="h-100">
                        <VCardText class="d-flex flex-column align-center">
                          <Gauge :value="averageManipulationScore"/>
                          <h2>Probably {{ manipulationDescription }}</h2>
                        </VCardText>
                      </VCard>
                    </VCol>
                  </VRow>
                </VContainer>


                <VDataTable :items="assessments" :headers="assessmentHeaders" class="bg-transparent" show-expand
                            hide-default-footer>
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
                  <template #item.credibility_score="{ item }">
                    <VProgressLinear :model-value="(item.credibility_score / 5)*100"
                                     :color="item.credibility_score > 3 ? 'success' : item.credibility_score > 1 ? 'warning' : 'error'"
                                     height="10" rounded/>
                  </template>
                  <template #item.manipulation_score="{ item }">
                    <VProgressLinear :model-value="(item.manipulation_score / 5)*100"
                                     :color="item.manipulation_score > 3 ? 'success' : item.manipulation_score > 1 ? 'warning' : 'error'"
                                     height="10" rounded/>
                  </template>
                  <template #item.timestamp="{ value }">
                    {{ formatDate(value) }}
                  </template>
                  <template #expanded-row="{ columns, item }">
                    <tr>
                      <td :colspan="columns.length" style="background-color: rgba(0,0,10,0.5)">
                        <VContainer fluid class="px-0">
                          <VRow>
                            <VCol cols="12">
                              <VCard variant="tonal" v-if="item.subjectCredential" title="Issued by">
                                <VCardText>
                                  <b>DID</b>: {{ item.subjectCredential.id }}<br>
                                  <b>Company</b>: {{ item.subjectCredential.company_name }}<br>
                                  <b>Website</b>: <a :href="item.subjectCredential.company_website"
                                                     target="_blank">{{ item.subjectCredential.company_website }}</a>
                                </VCardText>
                              </VCard>
                            </VCol>
                          </VRow>
                          <VRow>
                            <VCol cols="6" v-if="item.assessmentInfo?.credibility_evaluation">
                              <VCard variant="tonal" title="Credibility Evaluation">
                                <VCardText class="d-flex py-2">
                                  <div class="text-center mx-10 mt-2">
                                    <Gauge :value="item.assessmentInfo?.credibility_evaluation.score"/>
                                    <h2>{{
                                        getCredibilityDescription(item.assessmentInfo?.credibility_evaluation.score ?? 0)
                                      }}</h2>
                                  </div>
                                  <VTextarea class="my-auto" label="Comment"
                                             :model-value="item.assessmentInfo?.credibility_evaluation.note" no-resize
                                             rows="4"
                                             variant="outlined" readonly/>
                                </VCardText>
                              </VCard>
                            </VCol>
                            <VCol cols="6" v-if="item.assessmentInfo?.manipulation_evaluation">
                              <VCard variant="tonal" title="Manipulation Evaluation">
                                <VCardText class="d-flex py-2">
                                  <div class="text-center mx-10 mt-2">
                                    <Gauge :value="item.assessmentInfo?.manipulation_evaluation.score"/>
                                    <h2>{{
                                        getManipulationDescription(item.assessmentInfo?.manipulation_evaluation.score ?? 0)
                                      }}</h2>
                                  </div>
                                  <VTextarea label="Comment"
                                             :model-value="item.assessmentInfo?.manipulation_evaluation.note" no-resize
                                             rows="4"
                                             variant="outlined" readonly/>
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
import {storeToRefs} from "pinia";
import {onMounted, type Ref, ref} from "vue";
import {useRoute} from "vue-router";
import Gauge from "@/components/Gauge.vue";
import {useArticleStore} from "@/stores/article.ts";
import {useAssessmentStore} from "@/stores/assessment.ts";
import {
  CredibilityScore,
  type EbsiAssessmentDocument,
  type FactsSubjectCredential,
  type IndexedAssessment,
  ManipulationScore
} from "@/types";
import {extractSubjectCredential, formatDate} from "@/utility.ts";


const route = useRoute()

const articleStore = useArticleStore()
const assessmentStore = useAssessmentStore()

const {article} = storeToRefs(articleStore)
const {assessments} = storeToRefs(assessmentStore)

const claimedByPublisher = ref(undefined) as Ref<FactsSubjectCredential | undefined>

const averageCredibilityScore = ref(0)
const averageManipulationScore = ref(0)

const credibilityDescription = ref('')
const manipulationDescription = ref('')

const assessmentHeaders = [
  {title: 'Assessment ID', key: 'hash', value: (assessment: IndexedAssessment) => assessment.hash.slice(0, 10) + '...'},
  {title: 'Date', key: 'timestamp'},
  {title: 'Credibility Score', key: 'credibility_score'},
  {title: 'Manipulation Score', key: 'manipulation_score'},
  {title: 'DID Creator', key: 'creator'},
  {title: '', key: 'data-table-expand'},
]

async function expandAssessment(item: IndexedAssessment, expand: any) {
  const ebsi_document: EbsiAssessmentDocument = await assessmentStore.getAssessment(item.hash)
  item.assessmentInfo = ebsi_document.metadata.assessment_info
  item.subjectCredential = extractSubjectCredential(ebsi_document.metadata.fact_checker_vc)
  expand(item)
}

function getCredibilityDescription(average: number) {
  switch (average) {
    case CredibilityScore.FALSE: {
      return 'False'
    }
    case CredibilityScore.PARTIALLY_FALSE: {
      return 'Partially False'
    }
    case CredibilityScore.MISSING_CONTEXT: {
      return 'Missing Context'
    }
    case CredibilityScore.SUBJECTIVE: {
      return 'Subjective'
    }
    case CredibilityScore.TRUE: {
      return 'True'
    }
  }
  return ''
}

function getManipulationDescription(average: number) {
  switch (average) {
    case ManipulationScore.TOTALLY_MANIPULATED: {
      return 'Completely Manipulated'
    }
    case ManipulationScore.HEAVILY_MANIPULATED: {
      return 'Heavily Manipulated'
    }
    case ManipulationScore.PARTIALLY_MANIPULATED: {
      return 'Partially Manipulated'
    }
    case ManipulationScore.MINOR_EDITS: {
      return 'Minor Edits'
    }
    case ManipulationScore.AUTHENTIC: {
      return 'Authentic'
    }
  }
  return ''
}

onMounted(async () => {
  await articleStore.loadArticle(route.params.id as string)
  await assessmentStore.loadAssessmentsByArticle(route.params.id as string)
  if (articleStore.article)
    claimedByPublisher.value = extractSubjectCredential(articleStore.article.metadata.publisher_vc)

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
    credibilityDescription.value = getCredibilityDescription(Math.floor(averageCredibilityScore.value))
  }
  if (manipulationScoreCount > 0) {
    averageManipulationScore.value = manipulationScoreSum / manipulationScoreCount
    manipulationDescription.value = getManipulationDescription(Math.floor(averageManipulationScore.value))
  }
})
</script>