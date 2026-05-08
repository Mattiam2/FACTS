<template>
  <VContainer>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard>
          <VCardItem>
            <VCardTitle>Article list</VCardTitle>
          </VCardItem>
          <VCardText>
            <VDataTable :items="articles" :headers="articleHeaders">
              <template #item.actions="{ item }">
                <div class="d-flex ga-2">
                  <VBtn
                      @click.stop="openArticleWebsite(item)"
                  >Go to Website
                  </VBtn>
                  <VBtn
                      @click.stop="openArticleClaim(item)"
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
import {onMounted, ref} from "vue";
import AppLayout from "@/layouts/AppLayout.vue";
import router from "@/router";
import {useAppStore} from "@/stores/app.ts";

const appStore = useAppStore()
const articles = ref([])

const articleHeaders = [
  {title: 'Article ID', key: 'hash', value: (article: any) => article.hash.slice(0, 10) + '...'},
  {title: 'Date', key: 'timestamp'},
  {title: 'Url', key: 'url'},
  {title: 'DID Creator', key: 'creator'},
  {title: '', key: 'actions'},
]

function openArticleWebsite(article: any) {
  window.open(article.url, '_blank')
}

function openArticleClaim(article: any) {
  router.push(`/articles/${article.hash}`)
}

onMounted(async () => {
  articles.value = await appStore.getArticles()
})
</script>