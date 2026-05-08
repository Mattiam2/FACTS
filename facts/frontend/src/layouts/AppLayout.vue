<template>
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
              <b>Company</b>: {{ appStore.factsCredentialSubject?.company_name }}<br>
              <b>Role</b>: {{ appStore.factsCredentialSubject?.role }}<br>
              <b>DID</b>: {{ appStore.factsCredentialSubject?.id }}
              <VDivider class="my-3"/>
              <VBtn color="secondary">Logout</VBtn>
            </VCardText>
          </VCard>
        </VMenu>
      </VBtn>
    </template>
  </VAppBar>
  <VMain>
    <VContainer fluid>
      <slot/>
    </VContainer>
  </VMain>
</template>
<script setup lang="ts">
import {useAppStore} from "@/stores/app.ts";

const appStore = useAppStore()
</script>