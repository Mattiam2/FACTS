<template>
  <VContainer fluid>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard variant="tonal">
          <VCardItem>
            <VCardTitle>Access BackOffice</VCardTitle>
            <VCardSubtitle>Authenticate with your EBSI Wallet credentials</VCardSubtitle>
          </VCardItem>
          <VCardText v-if="!authStore.factsCredentialSubject">
            <VTextarea label="Verifiable Presentation" variant="outlined" v-model="vpToken"/>
            <VBtn color="primary" @click="validateVP">VALIDATE VP</VBtn>
          </VCardText>
          <VCardText v-if="authStore.factsCredentialSubject">
            <VCard class="mb-5" prepend-icon="mdi-shield-check" title="Credential Verified" variant="tonal">
              <VCardText>
                <b>Company</b>: {{ authStore.factsCredentialSubject.company_name }}<br>
                <b>Role</b>: {{ authStore.factsCredentialSubject.role }}<br>
                <b>DID</b>: {{ authStore.factsCredentialSubject.id }}
              </VCardText>
            </VCard>
            <VBtn color="primary" prepend-icon="mdi-wallet" :to="{path: '/wallet'}" v-if="!walletStore.ethWallet.ethAddress">Link Wallet</VBtn>
            <VBtn color="primary" class="mt-4" @click="completeLogin" v-if="walletStore.ethWallet.ethAddress">Go to home</VBtn>
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
import {useAuthStore} from "@/stores/auth.ts";
import {useWalletStore} from "@/stores/wallet.ts";

const appStore = useAppStore()
const authStore = useAuthStore()
const walletStore = useWalletStore()
const vpToken = ref('') as Ref<string>
const vcToken = ref('') as Ref<string>
const ethAddress = ref('') as Ref<string>

/**
 * Validates a Verifiable Presentation (VP) JWT provided by the user.
 * This method ensures the integrity of the token, parses its payload,
 * verifies the presence of required credentials, and processes user information
 * based on their role (e.g., publisher or fact checker). If valid, the user's
 * access token is requested based on a predefined scope.
 *
 * @return {boolean|void} Returns `false` if the VP JWT is invalid or if required
 *                        credentials are missing. Returns nothing upon successful validation.
 */
async function validateVP() {
  if (!vpToken.value.trim()) {
    appStore.addToastMessage('Please paste your Verifiable Presentation JWT', 'error')
    return
  }

  try {
    const parts = vpToken.value.split('.')
    if (parts.length !== 3) {
      appStore.addToastMessage('Invalid JWT format', 'error')
      vpToken.value = ''
      return false
    }
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))

    vcToken.value = payload.vp.verifiableCredential[0]

    if(!vcToken.value){
      appStore.addToastMessage('Invalid Verifiable Presentation JWT: Missing Credential', 'error')
      vpToken.value = ''
      return false
    }
    authStore.loadSubjectCredential(vcToken.value)

    let userScope = undefined
    if (authStore.factsCredentialSubject?.role == "publisher") {
      userScope = 'publisher_create'
    } else if (authStore.factsCredentialSubject?.role == "factChecker") {
      userScope = 'factchecker_create'
    } else {
      appStore.addToastMessage('Invalid Verifiable Presentation JWT: Invalid type', 'error')
      vpToken.value = ''
      return false
    }

    await authStore.requestFactsAccessToken(vpToken.value, userScope as string)

  } catch (error: any){
    console.error(error)
    appStore.addToastMessage(`Error during login: ${error.message}`, 'error')
    vpToken.value = ""
    vcToken.value = ""
    authStore.factsCredentialSubject = undefined
    return
  }
}

/**
 * Completes the login process by validating the ETH address, Verifiable Presentation,
 * and user's role, then redirects to the appropriate page based on the role.
 * Redirects to "Articles" for publishers and "Assessments" for other roles.
 *
 * @return {boolean} Returns false if validation fails; otherwise, the function redirects and does not return a value.
 */
function completeLogin() {
  if (!walletStore.ethWallet.ethAddress?.trim()) {
    appStore.addToastMessage('Please enter your ETH address', 'error')
    ethAddress.value = ''
    return false
  }
  if (!vcToken.value.trim()) {
    appStore.addToastMessage('Please validate your Verifiable Presentation first', 'error')
    ethAddress.value = ''
    return false
  }
  if (!authStore.factsCredentialSubject) {
    appStore.addToastMessage('Please validate your Verifiable Presentation first', 'error')
    ethAddress.value = ''
    return false
  }

  if(authStore.factsCredentialSubject.role == "publisher") {
    router.push('/articles')
  }else {
    router.push('/assessments')
  }
}
</script>

<style scoped>
</style>
