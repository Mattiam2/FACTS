<template>
  <VAppBar variant="tonal" :style="{ backgroundColor: 'rgba(var(--v-theme-surface), 0.90)' }">
    <VAppBarTitle class="text-green-accent-2 flex-0-0" style="font-size: 35px; font-weight: 900">
      <RouterLink to="/" class="text-decoration-none" style="color: inherit">F</RouterLink>
    </VAppBarTitle>
    <div class="d-flex flex-1-1 justify-center">
      <VBtn prepend-icon="mdi-home" :to="{path: '/'}" active-color="primary">Home</VBtn>
      <VBtn prepend-icon="mdi-newspaper" :to="{path: '/articles'}" active-color="primary">Articles</VBtn>
      <VBtn prepend-icon="mdi-account-group" :to="{path: '/assessments'}" active-color="primary">Assessments</VBtn>
    </div>
    <template #append>
      <VBtn prepend-icon="mdi-badge-account" color="primary" variant="tonal" class="me-2"
            v-if="authStore.factsCredentialSubject">
        <b>{{ authStore.factsCredentialSubject?.company_name }}</b>
        <VMenu activator="parent">
          <VCard rounded="lg" width="400" class="mt-1">
            <VCardText>
              <div class="d-flex align-center gap-2 mb-3">
                <v-icon icon="mdi-shield-check" color="primary" size="16"/>
                <span style="font-size:12px; font-weight:600; color:#00e5b4;">Credential Verified</span>
              </div>
              <b>Company</b>: {{ authStore.factsCredentialSubject?.company_name }}<br>
              <b>Role</b>: {{ authStore.factsCredentialSubject?.role }}<br>
              <b>DID</b>: {{ authStore.factsCredentialSubject?.id }}
            </VCardText>
          </VCard>
        </VMenu>
      </VBtn>
      <VBtn color="primary" variant="tonal" class="me-2" prepend-icon="mdi-wallet"
            v-if="walletStore.ethWallet.ethAddress">
        <b>Wallet Info</b>
        <VMenu activator="parent">
          <VCard rounded="lg" width="auto" class="mt-1">
            <VCardText>
              <b>ETH Address</b>: {{ walletStore.ethWallet.ethAddress }}
            </VCardText>
            <VCardActions>
              <VBtn variant="tonal" :to="{path: '/wallet'}" color="primary">Operations</VBtn>
              <VBtn variant="tonal" prepend-icon="mdi-link-variant-off"
                    @click="resetWalletStore()" color="primary">
                Unlink
              </VBtn>
            </VCardActions>
          </VCard>
        </VMenu>
      </VBtn>
      <VBtn color="primary" variant="tonal" class="me-2" :to="{path: '/login'}"
            v-if="!authStore.factsCredentialSubject">
        Login
      </VBtn>
      <VBtn color="primary" variant="tonal" class="me-2" :to="{path: '/wallet'}"
            v-if="!walletStore.ethWallet.ethAddress">
        Link Wallet
      </VBtn>
      <VBtn color="primary" variant="tonal" class="me-2" :to="{path: '/onboarding'}"
            v-if="!authStore.factsCredentialSubject">
        Request credential
      </VBtn>
      <VBtn color="secondary" variant="tonal" class="me-2" @click="logout" v-if="authStore.factsCredentialSubject">
        Logout
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
import {useAuthStore} from "@/stores/auth.ts";
import {useWalletStore} from "@/stores/wallet.ts";

const authStore = useAuthStore()
const walletStore = useWalletStore()

function resetWalletStore(){
  walletStore.$reset()
}

function logout() {
  authStore.$reset()
  walletStore.$reset()
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
  background: radial-gradient(ellipse at center, rgba(0, 229, 180, 0.2) 0%, transparent 90%);
  pointer-events: none;
  z-index: 0;
}
</style>