<template>
  <VDialog
      width="80%"
      v-model="isOpen"
  >
    <VCard
        width="100%"
        min-height="500"
        prepend-icon="mdi-certificate"
        title="Add Verification Method"
    >
      <VCardText>
        <VStepper v-model="addVMethodStep" :flat="true" elevation="0"
                  :items="['Provide VP', 'Get DIDR Write', 'Add Verification Method', 'Done']">
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
                Getting DIDR Write Scope...
              </div>
              <div v-else>
                DIDR Write Scope obtained, you can continue
              </div>
            </VSheet>
          </template>
          <template #item.3>
            <VSheet min-height="300">
              Complete DID onboarding adding an ES256 Verification Method:
              <VTextField label="Verification Method ID" v-model="vMethodId"/>
              <VTextField label="Public Key" placeholder="0x..." v-model="publicKey"/>
              <VCard subtitle="Relationship" variant="tonal" class="my-2">
                <VCardText>
                  <VCheckbox
                      v-model="vMethodRels"
                      label="Authentication"
                      value="authentication"
                      hide-details
                      density="compact"
                  />
                  <VCheckbox
                      v-model="vMethodRels"
                      label="Assertion Method"
                      value="assertionMethod"
                      hide-details
                      density="compact"
                  />
                  <VCheckbox
                      v-model="vMethodRels"
                      label="Capability Invocation"
                      value="capabilityInvocation"
                      hide-details
                      density="compact"
                  />
                  <VCheckbox
                      v-model="vMethodRels"
                      label="Key Agreement"
                      value="keyAgreement"
                      hide-details
                      density="compact"
                  />
                </VCardText>
              </VCard>
              <VCard subtitle="Algorithm" variant="tonal">
                <VCardText>
                  <VRadioGroup v-model="algorithmType" hide-details density="compact">
                    <VRadio label="ES256" value="ES256" class="my-2"/>
                    <VRadio label="ES256K" value="ES256K"/>
                  </VRadioGroup>
                </VCardText>
              </VCard>
            </VSheet>
          </template>
          <template #item.4>
            <VSheet min-height="300">
              <div v-if="!addVMethodCompleted">
                <VProgressCircular indeterminate/>
                {{ loadingText }}
              </div>
              <div v-else>
                <VIcon>mdi-check-circle</VIcon>
                Added Verification Method correctly
              </div>
            </VSheet>
          </template>
          <template #actions="{ prev, next }">
            <VStepperActions
                @click:next="addVMethodCustomNext(next)"
                :disabled="(addVMethodStep === 2 && !walletStore.ebsiAccessToken)"
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

const walletStore = useWalletStore()
const appStore = useAppStore()

const vpToken = ref('') as Ref<string>
const vMethodId = ref('') as Ref<string>
const addVMethodStep = ref(1) as Ref<number>
const subjectCredential = ref(undefined) as Ref<FactsSubjectCredential | undefined>
const txHash = ref('') as Ref<string>
const publicKey = ref('') as Ref<string>
const vMethodRels = ref<string[]>([])
const addVMethodCompleted = ref(false)
const algorithmType = ref('ES256') as Ref<string>
const loadingText = ref('Loading...')

const isOpen = computed({
  // getter
  get() {
    return model.value === 'verificationMethodAdd'
  },
  // setter
  set(newValue) {
    if (!newValue){
      vpToken.value = ''
      vMethodId.value = ''
      addVMethodStep.value = 1
      subjectCredential.value = undefined
      publicKey.value = ''
      vMethodRels.value = []
      addVMethodCompleted.value = false
      algorithmType.value = 'ES256'
      loadingText.value = 'Loading...'
    }
    model.value = newValue ? 'verificationMethodAdd' : undefined
  }
})

async function addVMethodCustomNext(next: () => void) {
  if (addVMethodStep.value == 1) {
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
    walletStore.requestEbsiAccessToken(vpToken.value, "didr_write")
    next()

  } else if (addVMethodStep.value == 2) {
    if (!subjectCredential.value) {
      appStore.addToastMessage("You've skipped step One!", 'error')
      return false
    }
    if (!walletStore.ebsiAccessToken) {
      appStore.addToastMessage('Please wait for the DIDR Write Access Token to be received', 'error')
      return false
    }
    next()
  } else if (addVMethodStep.value == 3) {
    if (!subjectCredential.value) {
      appStore.addToastMessage("You've skipped step One!", 'error')
      return false
    }
    if (!vMethodId.value.trim()) {
      appStore.addToastMessage('Please enter the verification method ID', 'error')
      return false
    }
    if (!publicKey.value.trim()) {
      appStore.addToastMessage('Please enter the verification method public key', 'error')
      return false
    }
    if (vMethodRels.value.length === 0) {
      appStore.addToastMessage('Please select at least one relationship', 'error')
      return false
    }
    next()
    loadingText.value = 'Creating addVerificationMethod transaction...'
    let response = await walletStore.createVerificationMethodTransaction(subjectCredential.value, vMethodId.value, publicKey.value, algorithmType.value == "ES256K")
    await sleep(1500)
    loadingText.value = 'Signing addVerificationMethod transaction...'
    const signedTransaction = await walletStore.signTransaction(response.result)
    await sleep(1500)
    loadingText.value = 'Confirming addVerificationMethod transaction...'
    response = await walletStore.confirmDidrTransaction(signedTransaction)
    txHash.value = response.result
    await sleep(1500)
    const vMethodAddedResult = response.result
    loadingText.value = 'Verification method added!'
    await sleep(1500)
    if (vMethodAddedResult) {
      for (const rel of vMethodRels.value) {
        txHash.value = ''
        loadingText.value = `Creating addVerificationRelationship transaction for ${rel}...`
        let response = await walletStore.createVerificationRelationshipTransaction(subjectCredential.value, vMethodId.value, rel)
        await sleep(1500)
        loadingText.value = `Signing addVerificationRelationship transaction for ${rel}...`
        const signedTransaction = await walletStore.signTransaction(response.result)
        await sleep(1500)
        loadingText.value = `Confirming addVerificationRelationship transaction for ${rel}...`
        response = await walletStore.confirmDidrTransaction(signedTransaction)
        txHash.value = response.result
        await sleep(1500)
        if (!txHash.value) {
          loadingText.value = `Error confirming addVerificationRelationship transaction for ${rel}!`
          continue
        }
      }
      addVMethodCompleted.value = true
    }
  }
}
</script>