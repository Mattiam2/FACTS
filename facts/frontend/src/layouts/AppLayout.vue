<template>
  <VAppBar>
    <VAppBarTitle class="text-green-accent-2 font-weight-bold">
      FACTS
    </VAppBarTitle>
    <VBtn color="primary" variant="tonal" class="me-2" :to="{path: '/articles'}">Articles</VBtn>
    <template #append>
      <VBtn color="primary" variant="tonal" class="me-2" v-if="appStore.factsCredentialSubject">
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
              <VBtn color="secondary" @click="logout">Logout</VBtn>
            </VCardText>
          </VCard>
        </VMenu>
      </VBtn>
      <VBtn color="primary" variant="tonal" class="me-2" :to="{path: '/login'}" v-else>
        Login
      </VBtn>
    </template>
  </VAppBar>
  <VMain style="background: #080d1a;">
    <div class="ambient-bg" aria-hidden="true"/>
    <VContainer fluid>
      <slot/>
    </VContainer>
  </VMain>
</template>
<script setup lang="ts">
import router from "@/router";
import {useAppStore} from "@/stores/app.ts";

const appStore = useAppStore()

function logout() {
  appStore.$reset()
  router.push('/login')
}

</script>
<style scoped>
.ambient-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: radial-gradient(ellipse at center, rgba(0, 229, 180, 0.05) 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}
</style>