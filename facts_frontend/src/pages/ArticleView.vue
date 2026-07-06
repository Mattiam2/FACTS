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
            <VCard v-if="articleStore.article" variant="tonal" title="Article">
              <VCardText>
                <b>URL</b>: <a :href="articleStore.article.metadata.article_info.url"
                               target="_blank">{{ articleStore.article.metadata.article_info.url }}</a><br>
                <b>Title</b>: {{ articleStore.article.metadata.article_info.title }}<br>
                <b>Author</b>: {{ articleStore.article.metadata.article_info.author }}<br>
                <b>Description</b>: {{ articleStore.article.metadata.article_info.description }}<br>
                <b>Publication Date</b>:
                {{ formatDate(articleStore.article.metadata.article_info.publication_date ?? '') }}<br>
                <b>Language</b>: {{ articleStore.article.metadata.article_info.language }}<br>
                <div
                    v-if="articleStore.article.metadata.article_info.sources && articleStore.article.metadata.article_info.sources.length > 0">
                  <b>Sources</b>:
                  <div v-for="source in articleStore.article.metadata.article_info.sources" :key="source"
                       class="d-flex ga-2">
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
                <div v-if="assessmentStore.assessments.length > 0 && assessmentStore.assessments[0].article_url"
                     class="mb-3">
                  <b>URL</b>: <a :href="assessmentStore.assessments[0].article_url"
                                 target="_blank">{{ assessmentStore.assessments[0].article_url }}</a>
                </div>
                <div v-if="assessmentStore.assessments.length > 0">
                  <VIcon class="me-1">mdi-alert</VIcon>
                  No publisher claim for this article, only fact-checking assessments found.
                </div>
                <div v-else>
                  <VIcon class="me-1">mdi-alert</VIcon>
                  No publisher claim for this article and no fact-checking assessments found.
                </div>
              </VCardText>
            </VCard>
            <VCard v-if="assessmentStore.assessments && assessmentStore.assessments.length > 0" class="mt-5"
                   title="Fact-checking assessments"
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


                <VDataTable :items="assessmentStore.assessments" :headers="assessmentHeaders" class="bg-transparent"
                            single-expand show-expand item-value="hash"
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
                        @click="expandAssessment(item, internalItem, toggleExpand)"
                    />
                  </template>
                  <template #item.credibility_score="{ item }">
                    <VProgressLinear :model-value="(item.credibility_score / 5)*100"
                                     :color="item.credibility_score > 3 ? 'success' : item.credibility_score > 1 ? 'warning' : 'error'"
                                     height="15" rounded><span style="color: black">{{ item.credibility_score }}</span>
                    </VProgressLinear>
                  </template>
                  <template #item.manipulation_score="{ item }">
                    <VProgressLinear :model-value="(item.manipulation_score / 5)*100"
                                     :color="item.manipulation_score > 3 ? 'success' : item.manipulation_score > 1 ? 'warning' : 'error'"
                                     height="15" rounded><span style="color: black">{{ item.manipulation_score }}</span>
                    </VProgressLinear>
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
            <VCard v-if="articleStore.article_sources.length > 0" class="mt-5" title="Source tree analysis"
                   variant="tonal">
              <VCardText>
                <VContainer>
                  <VRow v-if="sourcesAverageCredibilityScore > 0 || sourcesAverageManipulationScore > 0">
                    <VCol cols="6">
                      <VCard title="Average Credibility Score" variant="tonal" class="h-100">
                        <VCardText class="d-flex flex-column align-center">
                          <Gauge :value="sourcesAverageCredibilityScore"/>
                          <h2>Probably {{ sourcesCredibilityDescription }}</h2>
                        </VCardText>
                      </VCard>
                    </VCol>
                    <VCol cols="6">
                      <VCard title="Average Manipulation Score" variant="tonal" class="h-100">
                        <VCardText class="d-flex flex-column align-center">
                          <Gauge :value="sourcesAverageManipulationScore"/>
                          <h2>Probably {{ sourcesManipulationDescription }}</h2>
                        </VCardText>
                      </VCard>
                    </VCol>
                  </VRow>
                  <VRow>
                    <VCol cols="12">
                      <div v-for="sourceNode in articleStore.article_sources" :key="sourceNode.source_hash">
                        <VCard variant="tonal" class="my-2">
                          <VCardText>
                            <VRow>
                              <VCol cols="10">
                                <a :href="`/articles/${sourceNode.source_hash}`"
                                   v-if="sourceNode.source_value.startsWith('http')" class="text-decoration-none">
                                  <VIcon icon="mdi-link" color="primary" size="16"/>
                                  <span class="text-decoration-underline ms-1">{{ sourceNode.source_value }}</span>
                                </a>
                                <span v-else>{{ sourceNode.source_value }}</span>
                              </VCol>
                              <VCol cols="2"
                                    v-if="sourceNode.avg_credibility_score || sourceNode.avg_manipulation_score"
                                    class="d-flex justify-end">
                                <div class="mx-1" style="min-width: 50px">
                                  <VTooltip text="Credibility Score">
                                    <template #activator="{ props }">
                                      <VProgressLinear v-bind="props"
                                                       :model-value="(sourceNode.avg_credibility_score / 5)*100"
                                                       :color="sourceNode.avg_credibility_score > 3 ? 'success' : sourceNode.avg_credibility_score > 1 ? 'warning' : 'error'"
                                                       height="16" rounded v-if="sourceNode.avg_credibility_score"
                                                       style="cursor: pointer">
                                        <span style="color: black">{{ sourceNode.avg_credibility_score }}</span>
                                      </VProgressLinear>
                                    </template>
                                  </VTooltip>
                                </div>
                                <div class="mx-1" style="min-width: 50px">
                                  <VTooltip text="Manipulation Score">
                                    <template #activator="{ props }">
                                      <VProgressLinear v-bind="props"
                                                       :model-value="(sourceNode.avg_manipulation_score / 5)*100"
                                                       :color="sourceNode.avg_manipulation_score > 3 ? 'success' : sourceNode.avg_manipulation_score > 1 ? 'warning' : 'error'"
                                                       height="16" rounded v-if="sourceNode.avg_manipulation_score"
                                                       style="cursor: pointer">
                                        <span style="color: black">{{ sourceNode.avg_manipulation_score }}</span>
                                      </VProgressLinear>
                                    </template>
                                  </VTooltip>
                                </div>
                              </VCol>
                            </VRow>
                          </VCardText>
                        </VCard>
                      </div>
                    </VCol>
                  </VRow>
                </VContainer>
              </VCardText>
            </VCard>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
  </VContainer>
</template>

<script lang="ts" setup>
import type {
  EbsiAssessmentDocument,
  FactsSubjectCredential,
  IndexedAssessment,
  SourceNode
} from "@/types";
import {onMounted, type Ref, ref} from "vue";
import {useRoute} from "vue-router";
import Gauge from "@/components/Gauge.vue";
import {useAppStore} from "@/stores/app.ts";
import {useArticleStore} from "@/stores/article.ts";
import {useAssessmentStore} from "@/stores/assessment.ts";
import {
  extractSubjectCredential,
  formatDate,
  getCredibilityDescription,
  getManipulationDescription
} from "@/utility.ts";

const route = useRoute()

const appStore = useAppStore()
const articleStore = useArticleStore()
const assessmentStore = useAssessmentStore()

const claimedByPublisher = ref(undefined) as Ref<FactsSubjectCredential | undefined>

const averageCredibilityScore = ref(0)
const averageManipulationScore = ref(0)

const credibilityDescription = ref('')
const manipulationDescription = ref('')

const sourcesAverageCredibilityScore = ref(0)
const sourcesAverageManipulationScore = ref(0)

const sourcesCredibilityDescription = ref('')
const sourcesManipulationDescription = ref('')

const assessmentHeaders = [
  {title: 'Assessment ID', key: 'hash', value: (assessment: IndexedAssessment) => assessment.hash.slice(0, 10) + '...'},
  {title: 'Date', key: 'timestamp'},
  {title: 'Credibility Score', key: 'credibility_score'},
  {title: 'Manipulation Score', key: 'manipulation_score'},
  {title: 'DID Creator', key: 'creator'},
  {title: '', key: 'data-table-expand'},
]

/**
 * Expands an assessment by retrieving and populating additional assessment details.
 *
 * @param {IndexedAssessment} item - The assessment containing initial details and a hash for lookup.
 * @param {any} internalItem - An VDataTable internal data structure used for further processing.
 * @param {Function} expand - A callback function to process the expanded internal item.
 * @return {Promise<void>} A promise that resolves when the assessment has been expanded and processed.
 */
async function expandAssessment(item: IndexedAssessment, internalItem: any, expand: any) {
  const ebsi_document: EbsiAssessmentDocument = await assessmentStore.getAssessment(item.hash)
  item.assessmentInfo = ebsi_document.metadata.assessment_info
  item.subjectCredential = extractSubjectCredential(ebsi_document.metadata.fact_checker_vc)
  expand(internalItem)
}

/**
 * Loads an article using the provided hash and updates the relevant state.
 *
 * @param {string} hash - The unique identifier (hash) of the article to be loaded.
 * @return {Promise<void>} A promise that resolves when the article is successfully loaded
 */
async function loadArticle(hash: string) {
  try {
    await articleStore.loadArticle(hash)
    if (articleStore.article)
      claimedByPublisher.value = extractSubjectCredential(articleStore.article.metadata.publisher_vc)
  } catch (error: any) {
    console.error(error)
    appStore.addToastMessage(`Error loading article: ${error.message}`, 'error')
  }
}

/**
 * Loads assessments related to a specific article identified by its hash.
 *
 * @param {string} hash - The unique identifier (hash) of the article for which assessments will be loaded.
 * @return {Promise<void>} A promise that resolves when the assessments are successfully loaded
 */
async function loadAssessmentsByArticle(hash: string) {
  try {
    await assessmentStore.loadAssessmentsByArticle(hash)
  } catch (error: any) {
    console.error(error)
    appStore.addToastMessage(`Error loading assessments: ${error.message}`, 'error')
  }
}

/**
 * Loads the article sources from the article store using the provided hash.
 *
 * @param {string} hash - The unique identifier used to load the specific article sources.
 * @return {Promise<void>} A promise that resolves when the article sources are successfully loaded
 */
async function loadArticleSources(hash: string) {
  try {
    await articleStore.loadArticleSources(hash)
  } catch (error: any) {
    console.error(error)
    appStore.addToastMessage(`Error loading article sources: ${error.message}`, 'error')
  }
}

/**
 * Calculates average scores for credibility and manipulation based on the provided assessments.
 *
 * @param {IndexedAssessment[]} assessments - An array of assessment objects. Each object may contain
 * `credibility_score` and `manipulation_score` properties.
 * @return {void} Does not return a value
 */
function calculateAveragesFromAssessments(assessments: IndexedAssessment[]) {
  let credibilityScoreSum = 0
  let credibilityScoreCount = 0
  let manipulationScoreSum = 0
  let manipulationScoreCount = 0
  for (const assessment of assessments) {
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
}

/**
 * Calculates average credibility and manipulation scores from a collection of source nodes and updates related descriptors.
 *
 * @param {SourceNode[]} articleSources - An array of source nodes representing data sources. Each source node should contain properties `avg_credibility_score` and `avg_manipulation_score`.
 * @return {void} Does not return any value.
 */
function calculateAveragesFromSources(articleSources: SourceNode[]) {
  let sourcesCredibilityScoreSum = 0
  let sourcesCredibilityScoreCount = 0
  let sourcesManipulationScoreSum = 0
  let sourcesManipulationScoreCount = 0

  for (const sourceNode of articleSources) {
    if (sourceNode.avg_credibility_score) {
      sourcesCredibilityScoreSum += sourceNode.avg_credibility_score
      sourcesCredibilityScoreCount++
    }
    if (sourceNode.avg_manipulation_score) {
      sourcesManipulationScoreSum += sourceNode.avg_manipulation_score
      sourcesManipulationScoreCount++
    }
  }

  if (sourcesCredibilityScoreCount > 0) {
    sourcesAverageCredibilityScore.value = sourcesCredibilityScoreSum / sourcesCredibilityScoreCount
    sourcesCredibilityDescription.value = getCredibilityDescription(Math.floor(sourcesAverageCredibilityScore.value))
  }
  if (sourcesManipulationScoreCount > 0) {
    sourcesAverageManipulationScore.value = sourcesManipulationScoreSum / sourcesManipulationScoreCount
    sourcesManipulationDescription.value = getManipulationDescription(Math.floor(sourcesAverageManipulationScore.value))
  }
}

onMounted(async () => {
  articleStore.$reset()
  assessmentStore.$reset()
  await loadArticle(route.params.id as string)
  await loadAssessmentsByArticle(route.params.id as string)
  await loadArticleSources(route.params.id as string)
  calculateAveragesFromAssessments(assessmentStore.assessments)
  calculateAveragesFromSources(articleStore.article_sources)
})
</script>