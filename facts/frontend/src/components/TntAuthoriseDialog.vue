<template>
  <VDialog
      width="80%"
      v-model="isOpen"
  >
    <VCard
        width="100%"
        min-height="500"
        prepend-icon="mdi-certificate"
        title="Get whitelisted on Track and Trace"
    >
      <VCardText>
        <VStepper v-model="tntAuthoriseStep" :flat="true" elevation="0"
                  :items="['Provide VP', 'Get TNT Authorise', 'Sign transaction']">
          <template #item.1>
            <VSheet min-height="300">
              Please present a signed Verifiable Presentation onboarded on DID Registry
              <VTextarea label="VP Token" v-model="vpToken" class="mt-5" variant="outlined"/>
            </VSheet>
          </template>
          <template #item.2>
            <VSheet min-height="300">
              <div v-if="!walletStore.ebsiAccessToken">
                <VProgressCircular indeterminate/>
                Getting TNT Authorise Scope...
              </div>
              <div v-else>
                TNT Authorise Scope obtained, you can continue
              </div>
            </VSheet>
          </template>
          <template #item.3>
            <VSheet min-height="300">
              <div v-if="!tntAuthoriseCompleted">
                <VProgressCircular indeterminate/>
                {{ loadingText }}
              </div>
              <div v-else>
                DID is now whitelisted on TNT!<br>
                <VBtn class="mt-5" color="primary" @click="isOpen = false">Close</VBtn>
              </div>
            </VSheet>
          </template>
          <template #actions="{ prev, next }">
            <VStepperActions
                @click:next="tntAuthoriseCustomNext(next)"
                :disabled="disableStep"
                @click:prev="prev"/>
          </template>
        </VStepper>
      </VCardText>
    </VCard>
  </VDialog>
</template>

<script setup lang="ts">
import type {FactsSubjectCredential} from "@/types";
import {computed, type Ref, ref} from "vue";
import {useAppStore} from "@/stores/app.ts";
import {useWalletStore} from "@/stores/wallet.ts";
import {extractSubjectCredential, sleep} from "@/utility.ts";

const model = defineModel<string | undefined>()

const appStore = useAppStore()
const walletStore = useWalletStore()

const tntAuthoriseStep = ref(1) as Ref<number>
const vpToken = ref('') as Ref<string>
const subjectCredential = ref(undefined) as Ref<FactsSubjectCredential | undefined>
const txHash = ref('') as Ref<string>
const tntAuthoriseCompleted = ref(false)
const loadingText = ref('Loading...')

const disableStep = computed(() => {
  if (tntAuthoriseStep.value === 1) {
    return 'prev'
  }
  if (tntAuthoriseStep.value === 2 && !walletStore.ebsiAccessToken) {
    return 'next'
  }
  if (tntAuthoriseStep.value === 3) {
    return 'next'
  }
  return false
})

const isOpen = computed({
  // getter
  get() {
    return model.value === 'tntAuthorise'
  },
  // setter
  set(newValue) {
    if (!newValue) {
      tntAuthoriseStep.value = 1
      vpToken.value = ''
      subjectCredential.value = undefined
      txHash.value = ''
      tntAuthoriseCompleted.value = false
      loadingText.value = 'Loading...'
    }
    model.value = newValue ? 'tntAuthorise' : undefined
  }
})

async function tntAuthoriseCustomNext(next: () => void) {
  if (tntAuthoriseStep.value == 1) {
    if (!vpToken.value.trim()) {
      appStore.addToastMessage('Please enter the VP token', 'error')
      return false
    }
    const parts = vpToken.value.split('.')
    if (parts.length !== 3) {
      appStore.addToastMessage('Invalid JWT format', 'error')
      vpToken.value = ''
      return false
    }
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
    subjectCredential.value = extractSubjectCredential(payload.vp.verifiableCredential[0])
    walletStore.requestEbsiAccessToken(vpToken.value, "tnt_authorise").catch((error: any) => {
      console.error(error)
      appStore.addToastMessage(`Error requesting EBSI Access Token: ${error.message}`, 'error')
    })
    next()
  } else if (tntAuthoriseStep.value == 2) {
    if (!subjectCredential.value) {
      appStore.addToastMessage("You've skipped step One!", 'error')
      return false
    }
    if (!walletStore.ebsiAccessToken) {
      appStore.addToastMessage('Please wait for the TNT Authorise access token to be received', 'error')
      return false
    }
    next()
    loadingText.value = 'Creating authoriseDid transaction...'
    let response = undefined
    try {
      response = await walletStore.createAuthoriseDidTransaction(subjectCredential.value)
    }catch(error: any){
      console.error(error)
      appStore.addToastMessage(`Error creating authoriseDid transaction: ${error.message}`, 'error')
      return false
    }
    await sleep(1500)
    loadingText.value = 'Signing authoriseDid transaction...'
    let signedTransaction = undefined
    try {
      signedTransaction = await walletStore.signTransaction(response.result)
    }catch(error: any){
      console.error(error)
      appStore.addToastMessage(`Error signing authoriseDid transaction: ${error.message}`, 'error')
      return false
    }
    await sleep(1500)
    loadingText.value = 'Confirming authoriseDid transaction...'
    try {
      response = await walletStore.confirmTntTransaction(signedTransaction)
    }catch(error: any){
      console.error(error)
      appStore.addToastMessage(`Error confirming authoriseDid transaction: ${error.message}`, 'error')
      return false
    }
    await sleep(1500)
    txHash.value = response.result
    if (!txHash) {
      loadingText.value = `Error confirming authoriseDid transaction!`
      return false
    }
    tntAuthoriseCompleted.value = true
  }
}
</script>