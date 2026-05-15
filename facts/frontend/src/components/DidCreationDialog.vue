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
              <VTextField label="Verification Method ID" v-model="vMethodId"/>
              <div v-if="!transactionToSign">
                <VProgressCircular indeterminate/>
                Requesting transaction...
              </div>
              <div v-else-if="!txHash">
                <VBtn @click="signDidrTransaction">Sign transaction</VBtn>
              </div>
              <div v-else-if="txHash">
                DID created in DID Registry!<br/>
                Remember: To complete the onboarding correctly, you need to add an ES256 Verification Method with
                "authentication" and "assertionMethod" relationships.
              </div>
            </VSheet>
          </template>
          <template #actions="{ prev, next }">
            <VStepperActions
                @click:next="onboardingCustomNext(next)"
                :disabled="(onboardingStep === 2 && !walletStore.ebsiAccessToken)"
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
import {extractSubjectCredential} from "@/utility.ts";

const model = defineModel<string | undefined>()

const appStore = useAppStore()
const walletStore = useWalletStore()

const onboardingStep = ref(1) as Ref<number>
const vpToken = ref('') as Ref<string>
const vMethodId = ref('') as Ref<string>
const subjectCredential = ref(undefined) as Ref<FactsSubjectCredential | undefined>
const transactionToSign = ref(undefined) as Ref<object | undefined>
const txHash = ref('') as Ref<string>

const isOpen = computed({
  // getter
  get() {
    return model.value === 'didCreation'
  },
  // setter
  set(newValue) {
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
    walletStore.createDidDocumentTransaction(subjectCredential.value, vMethodId.value).then(response => {
      transactionToSign.value = response.result
    })
    next()
  }
}

async function signDidrTransaction() {
  if (!transactionToSign.value) {
    appStore.addToastMessage('No transaction to sign', 'error')
    return false
  }
  const signedTransaction = await walletStore.signTransaction(transactionToSign.value)
  const response = await walletStore.confirmDidrTransaction(signedTransaction)
  txHash.value = response.result
  return response.result
}

</script>