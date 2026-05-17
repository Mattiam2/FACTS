<template>
  <VDialog
      width="80%"
      v-model="isOpen"
  >
    <VCard
        width="100%"
        min-height="500"
        prepend-icon="mdi-certificate"
        title="EBSI Onboarding"
    >
      <VCardText>
        <VStepper v-model="onboardingStep" :flat="true" elevation="0"
                  :items="['Provide VP', 'Get DIDR Invite', 'Insert DID Document']">
          <template #item.1>
            <VSheet min-height="300">
              Please present a valid VerifiableAuthorisationToOnboard issued by Root TAO or TAO
              <VTextarea label="VP Token" v-model="vpToken" class="mt-5" variant="outlined"/>
            </VSheet>
          </template>

          <template #item.2>
            <VSheet min-height="300">
              <b>DID</b>: {{ subjectCredential?.id }}<br/>
              <b>Company</b>: {{ subjectCredential?.company_name }}<br/>
              <b>Role</b>: {{ subjectCredential?.role }}<br/><br/>

              <div v-if="!walletStore.ebsiAccessToken">
                <VProgressCircular indeterminate/>
                Getting DIDR Invite Access Token...
              </div>
              <div v-else>
                DIDR Invite Scope obtained, you can continue
              </div>
            </VSheet>
          </template>
          <template #item.3>
            <VSheet min-height="300">
              <div v-if="!didCreationCompleted">
                <VProgressCircular indeterminate/>
                {{ loadingText }}
              </div>
              <div v-else>
                DID created in DID Registry!<br/>
                Remember: To complete the onboarding correctly, you need to add an ES256 Verification Method with
                "authentication" and "assertionMethod" relationships.
              </div>
            </VSheet>
          </template>
          <template #actions="{ prev, next }">
            <VStepperActions
                @click:next="onboardingCustomNext(next)"
                :disabled="onboardingStep === 1 ? 'prev' : (onboardingStep === 2 && !walletStore.ebsiAccessToken)"
                @click:prev="prev"/>
          </template>
        </VStepper>
      </VCardText>
    </VCard>
  </VDialog>
</template>

<script setup lang="ts">
import type {FactsSubjectCredential} from "@/types";
import {computed, ref, type Ref} from "vue";
import {useAppStore} from "@/stores/app.ts";
import {useWalletStore} from "@/stores/wallet.ts";
import {extractSubjectCredential, sleep} from "@/utility.ts";

const model = defineModel<string | undefined>()

const appStore = useAppStore()
const walletStore = useWalletStore()

const onboardingStep = ref(1) as Ref<number>
const vpToken = ref('') as Ref<string>
const vMethodId = ref('') as Ref<string>
const subjectCredential = ref(undefined) as Ref<FactsSubjectCredential | undefined>
const didCreationCompleted = ref(false)
const txHash = ref('') as Ref<string>
const loadingText = ref('Loading...')

const isOpen = computed({
  // getter
  get() {
    return model.value === 'didCreation'
  },
  // setter
  set(newValue) {
    if (!newValue){
      onboardingStep.value = 1
      vpToken.value = ''
      vMethodId.value = ''
      subjectCredential.value = undefined
      txHash.value = ''
      didCreationCompleted.value = false
      loadingText.value = 'Loading...'
    }
    model.value = newValue ? 'didCreation' : undefined
  }
})

async function onboardingCustomNext(next: () => void) {
  if (onboardingStep.value == 1) {
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
    vMethodId.value = JSON.parse(atob(parts[0]))['kid'].split('#')[1]
    subjectCredential.value = extractSubjectCredential(payload.vp.verifiableCredential[0])
    walletStore.requestEbsiAccessToken(vpToken.value, "didr_invite")
    next()

  } else if (onboardingStep.value == 2) {
    if (!subjectCredential.value) {
      appStore.addToastMessage("You've skipped step One!", 'error')
      return false
    }
    if (!walletStore.ebsiAccessToken) {
      appStore.addToastMessage('Please wait for the DIDR Invite Access Token to be received', 'error')
      return false
    }
    next()
    loadingText.value = 'Creating DID Document transaction...'
    let response = await walletStore.createDidDocumentTransaction(subjectCredential.value, vMethodId.value)
    await sleep(1500)
    loadingText.value = 'Signing DID Document transaction...'
    const signedTransaction = await walletStore.signTransaction(response.result)
    await sleep(1500)
    if(!signedTransaction) {
      appStore.addToastMessage('Error signing DID Document transaction!', 'error')
      return false
    }
    loadingText.value = 'Confirming DID Document transaction...'
    response = await walletStore.confirmDidrTransaction(signedTransaction)
    await sleep(1500)
    txHash.value = response.result
    if(!txHash.value) {
      appStore.addToastMessage('Error confirming DID Document transaction!', 'error')
      return false
    }
    didCreationCompleted.value = true
  }
}
</script>