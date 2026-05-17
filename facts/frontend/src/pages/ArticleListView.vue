<template>
  <VContainer fluid>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard variant="tonal">
          <VCardItem>
            <VCardTitle>Article list</VCardTitle>
          </VCardItem>
          <VCardText>
            <VBtn color="primary" class="top-0 mt-5 mr-5 right-0 position-absolute" :to="{path: '/articles/submit'}"
                  v-if="authStore.factsCredentialSubject?.role == 'publisher'">Claim article
            </VBtn>
            <VDataTable :items="articles" :headers="articleHeaders" class="bg-transparent">
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
import type {IndexedArticle} from "@/types";
import {storeToRefs} from "pinia";
import {onMounted} from "vue";
import router from "@/router";
import {useArticleStore} from "@/stores/article.ts";
import {useAuthStore} from "@/stores/auth.ts";
import {formatDate} from "@/utility.ts";

const authStore = useAuthStore()
const articleStore = useArticleStore()

const {articles} = storeToRefs(articleStore)

const articleHeaders = [
  {title: 'Article ID', key: 'hash', value: (article: any) => article.hash.slice(0, 10) + '...'},
  {title: 'Date', key: 'timestamp'},
  {title: 'Url', key: 'url'},
  {title: 'DID Creator', key: 'creator'},
  {title: '', key: 'actions'},
]

function openArticleWebsite(article: IndexedArticle) {
  window.open(article.url, '_blank')
}

function openArticleClaim(article: IndexedArticle) {
  router.push(`/articles/${article.hash}`)
}

onMounted(async () => {
  await articleStore.loadArticles()
})
</script>