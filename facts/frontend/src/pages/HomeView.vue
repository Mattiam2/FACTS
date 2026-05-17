<template>
  <VContainer fluid>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <div class="text-center mb-15">
          <div class="facts-wordmark">
            FACTS
          </div>
          <div class="font-mono text-uppercase mb-5"
               style="font-size:12px; letter-spacing:3px; color: rgba(232,234,240,0.35); margin-top: -20px">
            Facts Authenticity & Credibility Tracking System
          </div>
          <div class="login-divider mx-auto mt-6"/>
        </div>
        <VTextField color="primary" placeholder="URL of an article..." v-model="articleUrl" variant="solo" hide-details style="max-width: 800px; margin: 0 auto">
          <template #append-inner>
            <VBtn color="primary" @click="searchArticle">SEARCH</VBtn>
          </template>
        </VTextField>
      </VCol>
    </VRow>
  </VContainer>
</template>

<script lang="ts" setup>
import type {EbsiArticleDocument} from "@/types";
import {ref} from "vue";
import router from "@/router";
import {useAppStore} from "@/stores/app.ts";
import {useArticleStore} from "@/stores/article.ts";

const articleStore = useArticleStore()
const appStore = useAppStore()
const articleUrl = ref("")

async function searchArticle() {
  const foundArticle: EbsiArticleDocument | undefined = await articleStore.getArticleByUrl(articleUrl.value)
  if (foundArticle) {
    await router.push(`/articles/${foundArticle.hash}`)
  }else {
    appStore.addToastMessage('Article not found', 'error')
  }
}
</script>

<style scoped>
.facts-wordmark {
  background: linear-gradient(to left, lightgreen, rgb(0, 229, 180), dodgerblue);
  -webkit-background-clip: text;
  color: transparent;
  font-weight: 900;
  font-size: 150px;
}
</style>