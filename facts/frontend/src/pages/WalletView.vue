<template>
  <VContainer>
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
                <VBtn @click="openEncapsulation" color="primary" class="ma-1">Create Verifiable Presentation</VBtn>
                <VBtn @click="openOnboardingEbsi" color="primary" class="ma-1">Onboard on EBSI DID Register</VBtn>
              </VCardText>
            </VCard>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
    <VDialog
        v-model="presentationRequestDialog"
        width="80%"
        title="Encapsulate Credential"
    >
      <VCard
          width="100%"
          min-height="500"
          prepend-icon="mdi-certificate"
      >
        <VCardText class="d-flex flex-column justify-center" v-if="!vpToken">
          <VTextarea label="VC Token" v-model="credentialToken" class="h-100" variant="outlined"/>
          <VTextField label="Verification ID" placeholder="Optional" v-model="verificationId"/>
          <VTextField label="Private key (will not leave your device)" placeholder="0x..." v-model="privateKey"/>
          <VRadioGroup label="Algorithm:" v-model="algorithmType">
            <VRadio label="ES256" value="ES256"/>
            <VRadio label="ES256K" value="ES256K"/>
          </VRadioGroup>
          <VBtn @click="createVP" color="primary" class="my-2">Encapsulate</VBtn>
        </VCardText>
        <VCardText v-if="vpToken" class="d-flex flex-column">
          This is your Verifiable Presentation Token. Please store in a safe place.
          <VTextarea label="VP Token" v-model="vpToken" variant="outlined" class="mt-5" readonly/>
          <VBtn :to="{path: '/login'}" color="primary" v-if="verificationId">Go to Login</VBtn>
          <VBtn color="primary" v-else>Onboard on DID Registry</VBtn>
        </VCardText>
      </VCard>
    </VDialog>
    <VDialog
        v-model="onboardingEbsiDialog"
        width="80%"
        title="EBSI Onboarding"
    >
      <VCard
          width="100%"
          min-height="500"
          prepend-icon="mdi-certificate"
      >
        <VCardText>
          <VStepper v-model="onboardingStep" :flat="true" elevation="0"
                    :items="['Provide VP', 'Get DIDR Invite', 'Insert DID Document', 'Get DIDR Write', 'Add Verification Method', 'Done']">
            <template #item.1>
              <VSheet min-height="300">
                Please present a valid VerifiableAuthorisationToOnboard issued by Root TAO or TAO
                <VTextarea label="VP Token" v-model="vpToken" class="mt-5" variant="outlined"/>
              </VSheet>
            </template>

            <template #item.2>
              <VSheet min-height="300">
                <VProgressCircular indeterminate/>
                Getting DIDR Invite Access Token...
              </VSheet>
            </template>
            <template #item.3>
              <VSheet min-height="300">
                <VProgressCircular indeterminate/>
                Signing DID Document creation transaction...
              </VSheet>
            </template>
            <template #item.4>
              <VSheet min-height="300">
                <VProgressCircular indeterminate/>
                Getting DIDR Write Scope...
              </VSheet>
            </template>
            <template #item.5>
              <VSheet min-height="300">
                <VTextField label="Verification Method ID"/>
                <VTextField label="ES256 Public Key" placeholder="0x..."/>
              </VSheet>
            </template>
            <template #item.6>
              <VSheet min-height="300">
                <VIcon>mdi-check-circle</VIcon>
                You've successfully onboarded on EBSI!<br><br>
                <b>Next step:</b> Create a new VP with your current credential signed with an ES256 verification method.
              </VSheet>
            </template>
            <template #actions="{ prev, next }">
              <VStepperActions
                @click:next="next"
                @click:prev="prev">
              </VStepperActions>
            </template>
          </VStepper>
        </VCardText>
      </VCard>
    </VDialog>
  </VContainer>
</template>

<script lang="ts" setup>
import type {VerifiablePresentation, VPPayload} from "@/types";
import {hexToBytes} from '@noble/curves/abstract/utils'
import {p256} from '@noble/curves/p256';
import {secp256k1} from '@noble/curves/secp256k1'
import {type Ref, ref} from "vue";
import {useAppStore} from "@/stores/app.ts";
import {useWalletStore} from "@/stores/wallet.ts";

const appStore = useAppStore()
const walletStore = useWalletStore()

const onboardingStep = ref(1) as Ref<number>
const ethAddress = ref('')
const ethPrivateKey = ref('')

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

const presentationRequestDialog = ref(false)
const onboardingEbsiDialog = ref(false)
const credentialToken = ref('')
const privateKey = ref('')
const verificationId = ref('')
const vpToken = ref('')

const algorithmType = ref('ES256') as Ref<string>

function openEncapsulation() {
  presentationRequestDialog.value = true
}

function openOnboardingEbsi() {
  onboardingEbsiDialog.value = true
  presentationRequestDialog.value = false
}

function getDataFromVcToken(vcToken: string): { iss: string, sub: string } {
  const [, payloadB64] = vcToken.split('.');
  const payload = JSON.parse(atob(payloadB64.replace(/-/g, '+').replace(/_/g, '/')));
  if (!payload.iss) {
    appStore.addToastMessage('VC Token JWT has no "iss" claim', 'error')
    throw new Error('vc_token JWT has no "iss" claim');
  }
  return {iss: payload.iss, sub: payload.sub};
}


function base64url(input: Uint8Array | string): string {
  const bytes =
      typeof input === 'string'
          ? new TextEncoder().encode(input)
          : input;

  return btoa(String.fromCodePoint(...bytes))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/g, '')
}

async function signJwt(
    header: object,
    payload: object,
    privateKeyHex: string
) {
  // JWT parts
  const encodedHeader = base64url(
      JSON.stringify(header)
  );

  const encodedPayload = base64url(
      JSON.stringify(payload)
  );

  const signingInput =
      `${encodedHeader}.${encodedPayload}`;

  // SHA-256 hash
  const hashBuffer = await crypto.subtle.digest(
      'SHA-256',
      new TextEncoder().encode(signingInput)
  );

  const hash = new Uint8Array(hashBuffer);

  const privKeyBytes = hexToBytes(privateKeyHex.replace('0x', ''))

  const signature = algorithmType.value == 'ES256' ? p256.sign(hash, privKeyBytes) : secp256k1.sign(hash, privKeyBytes);
  const sigBytes = signature.toCompactRawBytes() // 64 bytes: r(32) + s(32)

  const encodedSignature = btoa(String.fromCodePoint(...sigBytes))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '')

  return `${signingInput}.${encodedSignature}`;
}

async function createVP() {
  if (!credentialToken.value.trim()) {
    appStore.addToastMessage('Please enter the credential token', 'error')
    return false
  }
  if (!privateKey.value.trim()) {
    appStore.addToastMessage('Please enter your private key', 'error')
    return false
  }

  const data = getDataFromVcToken(credentialToken.value)
  if (!data) {
    appStore.addToastMessage('Invalid credential token', 'error')
    return false
  }

  const urnStr = `urn:uuid:${crypto.randomUUID()}`;
  const now = Math.floor(Date.now() / 1000);

  const vp: VerifiablePresentation = {
    '@context': ['https://www.w3.org/2018/credentials/v1'],
    id: urnStr,
    type: ['VerifiablePresentation'],
    holder: data.sub,
    verifiableCredential: credentialToken.value ? [credentialToken.value] : [],
  };

  const payload: VPPayload = {
    iss: data.sub,
    aud: data.iss,
    sub: data.sub,
    iat: now,
    nbf: now,
    exp: now + 10 * 365 * 24 * 60 * 60,
    nonce: urnStr,
    jti: urnStr,
    vp: vp,
  };

  const privateKeyHex = privateKey.value.replace(/^0x/i, '');

  const headers: { typ: string, alg: string, kid?: string } = {typ: 'JWT', alg: algorithmType.value};
  if (verificationId.value) headers['kid'] = verificationId.value;

  vpToken.value = await signJwt(
      headers,
      payload,
      privateKeyHex
  )

}

async function onboardOnDidRegistry() {
  if (!vpToken.value.trim()) {
    appStore.addToastMessage('Please enter the VP token', 'error')
    return false
  }
  if (!privateKey.value.trim()) {
    appStore.addToastMessage('Please enter your private key', 'error')
  }
}
</script>

<style scoped>
</style>
