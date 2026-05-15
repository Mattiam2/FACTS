<template>
  <VDialog
      width="80%"
      v-model="isOpen"
  >
    <VCard
        width="100%"
        min-height="500"
        prepend-icon="mdi-certificate"
        title="Encapsulate Credential"
    >
      <VCardText class="d-flex flex-column justify-center" v-if="!vpToken">
        <VTextarea label="VC Token" v-model="credentialToken" class="h-100" variant="outlined"/>
        <VTextField label="Verification ID" v-model="verificationId"/>
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
        <VBtn color="primary">Close</VBtn>
      </VCardText>
    </VCard>
  </VDialog>
</template>

<script setup lang="ts">
import type {VerifiablePresentation, VPPayload} from "@/types";
import {hexToBytes} from "@noble/curves/abstract/utils";
import {p256} from "@noble/curves/p256";
import {secp256k1} from "@noble/curves/secp256k1";
import {computed, type Ref, ref} from "vue";
import {useAppStore} from "@/stores/app.ts";

const model = defineModel<string | undefined>()

const appStore = useAppStore()

const credentialToken = ref('')
const privateKey = ref('')
const verificationId = ref('')
const algorithmType = ref('ES256') as Ref<string>
const vpToken = ref('') as Ref<string>

const isOpen = computed({
  // getter
  get() {
    return model.value === 'presentationRequest'
  },
  // setter
  set(newValue) {
    model.value = newValue ? 'presentationRequest' : undefined
  }
})

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


  let privKeyBytes = hexToBytes(privateKeyHex.replace('0x', ''))
  if (algorithmType.value == 'ES256') {
    const privKeyString = new TextDecoder().decode(privKeyBytes)
    const privKeyJWK = JSON.parse(privKeyString)
    const dStr = atob(privKeyJWK.d.replace(/-/g, '+').replace(/_/g, '/'));
    privKeyBytes = Uint8Array.from(dStr, c => c.codePointAt(0) ?? 0);
  }

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
  if (!verificationId.value.trim()) {
    appStore.addToastMessage('Please enter the verification ID', 'error')
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

  const headers: { typ: string, alg: string, kid?: string } = {
    typ: 'JWT',
    alg: algorithmType.value,
    kid: data.sub + '#' + verificationId.value
  };

  vpToken.value = await signJwt(
      headers,
      payload,
      privateKeyHex
  )

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
</script>