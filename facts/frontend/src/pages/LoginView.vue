<template>
  <VContainer>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard>
          <VCardItem>
            <VCardTitle>Access BackOffice</VCardTitle>
            <VCardSubtitle>Authenticate with your EBSI Wallet credentials</VCardSubtitle>
          </VCardItem>
          <VCardText v-if="!appStore.factsCredentialSubject">
            <VTextarea label="Verifiable Presentation" variant="outlined" v-model="vpToken"/>
            <VBtn color="primary" @click="validateVP">VALIDATE VP</VBtn>
          </VCardText>
          <VCardText v-if="appStore.vcToken && appStore.factsCredentialSubject">
            <VCard class="mb-5">
              <VCardText>
                <div class="d-flex align-center gap-2 mb-3">
                  <v-icon icon="mdi-shield-check" color="primary" size="16"/>
                  <span style="font-size:12px; font-weight:600; color:#00e5b4;">Credential Verified</span>
                </div>
                <b>Company</b>: {{ appStore.factsCredentialSubject.company_name }}<br>
                <b>Role</b>: {{ appStore.factsCredentialSubject.role }}<br>
                <b>DID</b>: {{ appStore.factsCredentialSubject.id }}
              </VCardText>
            </VCard>
            <VCard>
              <VCardText>
                <VTextField label="ETH Address" placeholder="0x..." class="mb-2" hide-details v-model="ethAddress"/>
              </VCardText>
            </VCard>
            <VBtn color="primary" class="mt-4" @click="validateWallet">SIGN IN</VBtn>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
  </VContainer>
</template>

<script lang="ts" setup>
import {type Ref, ref} from "vue";
import router from "@/router";
import {useAppStore} from "@/stores/app.ts";

const appStore = useAppStore()
const vpToken = ref('') as Ref<string>
const ethAddress = ref('') as Ref<string>

async function validateVP() {
  if (!vpToken.value.trim()) {
    appStore.addToastMessage('Please paste your Verifiable Presentation JWT', 'error')
    return
  }

  try {
    const parts = vpToken.value.split('.')
    if (parts.length !== 3) {
      appStore.addToastMessage('Invalid JWT format', 'error')
      return
    }
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))

    appStore.vcToken = payload.vp.verifiableCredential[0]

    if(!appStore.vcToken){
      appStore.addToastMessage('Invalid Verifiable Presentation JWT: Missing Credential', 'error')
      return
    }
    appStore.factsCredentialSubject = appStore.extractSubjectCredential(appStore.vcToken)

    let userScope = undefined
    if (appStore.factsCredentialSubject?.role == "PUBLISHER") {
      userScope = 'publisher_create'
    } else if (appStore.factsCredentialSubject?.role == "FACT CHECKER") {
      userScope = 'factchecker_create'
    }

    await appStore.requestAccessToken(vpToken.value, userScope as string)

  } catch {
    appStore.addToastMessage('Invalid or malformed Verifiable Presentation JWT', 'error')
    return
  }
}

function validateWallet () {
  if (!ethAddress.value.trim()) {
    appStore.addToastMessage('Please enter your ETH address and private key', 'error')
    return
  }
  if (!appStore.vcToken) {
    appStore.addToastMessage('Please validate your Verifiable Presentation first', 'error')
  }
  if (!appStore.factsCredentialSubject) {
    appStore.addToastMessage('Please validate your Verifiable Presentation first', 'error')
  }
  if (!appStore.vcToken || !appStore.factsCredentialSubject) return
  appStore.ethWalletAddress = ethAddress.value
  if(appStore.factsCredentialSubject.role == "PUBLISHER")
    router.push('/articles/submit')
  else
    router.push('/assessments/submit')
}
</script>

<style scoped>
</style>
