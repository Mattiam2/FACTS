<template>
  <VAppBar>
    <VAppBarTitle class="text-green-accent-2" style="font-size: 35px; font-weight: 900">
      <RouterLink to="/" class="text-decoration-none" style="color: inherit">F</RouterLink>
    </VAppBarTitle>
    <div class="flex-grow-1">
      <VBtn icon="mdi-home" :to="{path: '/'}" active-color="primary"/>
      <VBtn icon="mdi-newspaper" :to="{path: '/articles'}" active-color="primary"/>
      <VBtn icon="mdi-account-group" :to="{path: '/assessments'}" active-color="primary"/>
    </div>
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
            </VCardText>
          </VCard>
        </VMenu>
      </VBtn>
      <VBtn color="secondary" variant="tonal" class="me-2" @click="logout" v-if="appStore.factsCredentialSubject">Logout</VBtn>
      <VBtn color="primary" variant="tonal" class="me-2" :to="{path: '/login'}" v-if="!appStore.factsCredentialSubject">
        Login
      </VBtn>
      <VBtn color="primary" variant="tonal" class="me-2" :to="{path: '/onboarding'}" v-if="!appStore.factsCredentialSubject">
        Onboarding
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