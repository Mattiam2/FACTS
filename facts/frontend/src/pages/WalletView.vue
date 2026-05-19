<template>
  <VContainer fluid>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard variant="tonal">
          <VCardItem>
            <VCardTitle>Wallet</VCardTitle>
            <VCardSubtitle>EBSI Wallet operations</VCardSubtitle>
          </VCardItem>
          <VCardText>
            <VCard title="Wallet link" prepend-icon="mdi-ethereum" variant="tonal"
                   v-if="!walletStore.ethWallet.ethAddress">
              <VCardText>
                <VTextField label="ETH Address" placeholder="0x..." class="mb-2" variant="outlined" hide-details
                            v-model="ethAddress"/>
                <VTextField label="ETH Private Key" type="password" placeholder="0x..." class="mb-2"
                            variant="outlined"
                            v-model="ethPrivateKey"
                            hide-details/>
                <VBtn @click="linkWallet" color="primary">Link Wallet</VBtn>
              </VCardText>
            </VCard>
            <VCard title="ETH Address" prepend-icon="mdi-wallet" variant="tonal" v-else>
              <VCardText>
                {{ walletStore.ethWallet.ethAddress }}
              </VCardText>
            </VCard>
            <VCard title="Operations" variant="tonal" class="my-4" v-if="walletStore.ethWallet.ethAddress">
              <VCardText>
                <VBtn @click="openEncapsulation" color="primary" class="ma-1">Create
                  Verifiable Presentation
                </VBtn>
                <VBtn @click="openOnboardingEbsi" color="primary" class="ma-1">
                  Onboard on EBSI DID Register
                </VBtn>
                <VBtn @click="openVerificationMethodCreation" color="primary" class="ma-1">
                  Add Verification Method
                </VBtn>
                <VBtn @click="openAuthoriseDid" color="primary" class="ma-1">
                  Onboard on EBSI Track and Trace
                </VBtn>
              </VCardText>
            </VCard>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
    <PresentationRequestDialog v-model="openedDialog"/>
    <DidCreationDialog v-model="openedDialog"/>
    <VerificationMethodAddDialog v-model="openedDialog"/>
    <TntAuthoriseDialog v-model="openedDialog"/>
  </VContainer>
</template>

<script lang="ts" setup>
import {type Ref, ref} from "vue";
import DidCreationDialog from "@/components/DidCreationDialog.vue";
import PresentationRequestDialog from "@/components/PresentationRequestDialog.vue";
import TntAuthoriseDialog from "@/components/TntAuthoriseDialog.vue";
import VerificationMethodAddDialog from "@/components/VerificationMethodAddDialog.vue";
import {useAppStore} from "@/stores/app.ts";
import {useAuthStore} from "@/stores/auth.ts";
import {useWalletStore} from "@/stores/wallet.ts";

const appStore = useAppStore()
const walletStore = useWalletStore()

const ethAddress = ref('')
const ethPrivateKey = ref('')
const openedDialog = ref(undefined) as Ref<'presentationRequest' | 'didCreation' | 'verificationMethodAdd' | 'tntAuthorise' | undefined>

function linkWallet() {
  if (!ethAddress.value.trim()) {
    appStore.addToastMessage('Please enter your ETH address', 'error')
    return false
  }
  if (!ethPrivateKey.value.trim()) {
    appStore.addToastMessage('Please enter your ETH private key', 'error')
    return false
  }
  walletStore.linkWallet(ethAddress.value, ethPrivateKey.value)
}

function openEncapsulation() {
  walletStore.ebsiAccessToken = undefined
  openedDialog.value = 'presentationRequest'
}

function openOnboardingEbsi() {
  walletStore.ebsiAccessToken = undefined
  openedDialog.value = 'didCreation'
}

function openVerificationMethodCreation() {
  walletStore.ebsiAccessToken = undefined
  openedDialog.value = 'verificationMethodAdd'
}

function openAuthoriseDid() {
  walletStore.ebsiAccessToken = undefined
  openedDialog.value = 'tntAuthorise'
}
</script>

<style scoped>
</style>
