<template>
  <VContainer fluid>
    <VAppBar>
      <VAppBarTitle>
        FACTS: Publisher
      </VAppBarTitle>
      <template #append>
        <VBtn color="primary" variant="tonal" class="me-2">
          <VIcon>mdi-badge-account</VIcon>
          <b>{{ appStore.factsCredentialSubject?.company_name }}</b>
          <VMenu activator="parent">
            <VCard rounded="lg" width="400" class="mt-1">
              <VCardText>
                <div class="d-flex align-center gap-2 mb-3">
                  <v-icon icon="mdi-shield-check" color="primary" size="16"/>
                  <span style="font-size:12px; font-weight:600; color:#00e5b4;">Credential Verified</span>
                </div>
                <b>Role</b>: {{ appStore.factsCredentialSubject?.role }}<br>
                <b>DID</b>: {{ appStore.factsCredentialSubject?.id }}
              </VCardText>
            </VCard>
          </VMenu>
        </VBtn>
      </template>
    </VAppBar>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard>
          <VCardItem>
            <VCardTitle>Claim an Article</VCardTitle>
            <VCardSubtitle>Publish an article to FACTS for authenticity verification.</VCardSubtitle>
          </VCardItem>
          <VCardText>
            <div class="d-flex flex-column ga-3">
              <VTextField label="Canonical URL" variant="outlined" prepend-inner-icon="mdi-link"
                          v-model="article_url"
                          hide-details/>
              <VTextField label="Article Title" variant="outlined" prepend-inner-icon="mdi-format-title"
                          v-model="article_title"
                          hide-details/>
              <VTextField label="Article Author(s)" variant="outlined"
                          v-model="article_author"
                          prepend-inner-icon="mdi-account-edit" hide-details/>
              <VTextarea label="Description" variant="outlined" prepend-inner-icon="mdi-text"
                         v-model="article_description"
                         hide-details/>
              <VDateInput
                  label="Publication Date"
                  prepend-icon=""
                  prepend-inner-icon="mdi-calendar"
                  variant="outlined"
                  v-model="article_publication_date"
                  hide-details
              />
              <VSelect
                  label="Language"
                  prepend-inner-icon="mdi-translate"
                  variant="outlined"
                  v-model="article_language"
                  :items="['BG', 'CS', 'DA', 'DE', 'EL', 'EN', 'ES', 'ET', 'FI', 'FR', 'GA', 'HR', 'HU', 'IT', 'LT', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SL', 'SV']"
              />
            </div>
            <VBtn color="primary" @click="requestArticleCreation">Request</VBtn>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
  </VContainer>
</template>

<script lang="ts" setup>
import type {ArticleInfo} from "@/types";
import {ref} from "vue";
import {useAppStore} from "@/stores/app.ts";

const appStore = useAppStore()

const article_url = ref('')
const article_title = ref('')
const article_author = ref('')
const article_description = ref('')
const article_publication_date = ref('')
const article_language = ref('')

async function requestArticleCreation () {
  const article: ArticleInfo = {
    url: article_url.value,
    title: article_title.value,
    author: article_author.value,
    description: article_description.value,
    publication_date: article_publication_date.value,
    language: article_language.value,
    sources: []
  }
  const response = await appStore.createArticleTransaction(article)
  appStore.addToastMessage(`Received: ${response}`, 'success')
}
</script>