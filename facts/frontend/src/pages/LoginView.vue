<template>
  <VContainer fluid>
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
                <VTextField label="ETH Private Key" placeholder="0x..." type="password" class="my-2" v-model="ethPrivateKey" hide-details/>
                <VIcon icon="mdi-lock-outline" size="12"/> Your private key never leaves this device.
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
const ethPrivateKey = ref('') as Ref<string>

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

    const vcData = JSON.parse(atob(payload.vp.verifiableCredential[0].split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))).vc

    if (!vcData.type.includes('VerifiableCredential') || !vcData.type.includes('FACTSFactCheckerCredential') && !vcData.type.includes('FACTSPublisherCredential')) {
      appStore.addToastMessage('Invalid Verifiable Presentation type', 'error')
      return
    }

    let userScope = undefined
    let role = undefined
    if (vcData.type.includes('FACTSPublisherCredential')) {
      userScope = 'publisher_create'
      role = "PUBLISHER"
    } else if (vcData.type.includes('FACTSFactCheckerCredential')) {
      userScope = 'factchecker_create'
      role = "FACT CHECKER"
    }

    await appStore.requestAccessToken(vpToken.value, userScope as string)

    appStore.factsCredentialSubject = payload?.vp?.verifiableCredential?.[0]
        ? JSON.parse(atob(payload.vp.verifiableCredential[0].split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))).vc?.credentialSubject
        : payload?.vc?.credentialSubject
    if (appStore.factsCredentialSubject)
      appStore.factsCredentialSubject.role = role
  } catch {
    appStore.addToastMessage('Invalid or malformed Verifiable Presentation JWT', 'error')
    return
  }
}

function validateWallet () {
  if (!ethAddress.value.trim() || !ethPrivateKey.value.trim()) {
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
  appStore.ethWallet = { eth_address: ethAddress.value, eth_private_key: ethPrivateKey.value }
  if(appStore.factsCredentialSubject.role == "PUBLISHER")
    router.push('/articles/submit')
  else
    router.push('/assessments/submit')
}
</script>

<style scoped>
</style>
