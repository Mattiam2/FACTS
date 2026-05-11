<template>
  <VContainer>
    <VRow justify="center" align="center">
      <VCol cols="12">
        <VCard>
          <VCardItem>
            <VCardTitle>Onboard on EBSI</VCardTitle>
            <VCardSubtitle>Request a Credential to FACTS Issuer</VCardSubtitle>
          </VCardItem>
          <VCardText>
            What is your role?
            <div class="mt-2">
              <VRow>
                <VCol cols="6">
                  <VBtn prepend-icon="mdi-newspaper" color="secondary"
                        @click="setRole('publisher')"
                        :active="subjectRole == 'publisher'"
                        height="100" block stacked>
                    I am a Publisher
                  </VBtn>
                </VCol>
                <VCol cols="6">
                  <VBtn prepend-icon="mdi-head-check" color="secondary"
                        @click="setRole('factChecker')"
                        :active="subjectRole == 'factChecker'"
                        height="100" block stacked>
                    I am a Fact Checker
                  </VBtn>
                </VCol>
              </VRow>
            </div>
          </VCardText>
          <VCardText v-if="subjectRole">
            <VTextField label="DID" v-model="subjectDid"/>
            <VTextField label="Company Name" v-model="subjectCompanyName"/>
            <VTextField label="Company Address" v-model="subjectCompanyAddress"/>
            <VTextField label="Company VAT" v-model="subjectCompanyVat"/>
            <VTextField label="Company Website" v-model="subjectCompanyWebsite"/>
            <VTextField label="Company Email" v-model="subjectCompanyEmail"/>
            <VTextField label="Company Country" v-model="subjectCompanyCountry"/>
            <VTextField label="Specialization" v-model="subjectSpecialization"/>
            <VTextField label="Accredited By" v-if="subjectRole == 'factChecker'" v-model="subjectAccreditedBy"/>
            <VCard v-if="subjectRole == 'publisher'" title="Authorized Hosts" variant="tonal" class="mb-5">
              <VCardText>
                <div v-for="(item, index) in subjectAuthorizedHosts" :key="index" class="d-flex align-center my-5">
                  <VTextField
                      v-model="subjectAuthorizedHosts[index]"
                      :label="'Authorized host ' + (index + 1)"
                      density="compact"
                      variant="outlined"
                      hide-details
                      max-width="800"
                      class="mr-2"
                      placeholder="domain.com"
                  />
                  <VBtn icon="mdi-delete" @click="subjectAuthorizedHosts.splice(index, 1)"
                        v-if="subjectAuthorizedHosts.length > 1" color="bg-red" class="me-2" density="compact"/>
                </div>
                <VBtn @click="subjectAuthorizedHosts.push('')" color="primary" density="compact">Add</VBtn>
              </VCardText>
            </VCard>
            <VBtn color="primary" @click="requestCredential">REQUEST VC</VBtn>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
    <VDialog
        v-model="credentialRequestDialog"
        width="80%"
        title="Credential Received"
        persistent
    >
      <VCard
          width="100%"
          min-height="500"
          prepend-icon="mdi-certificate"
      >
        <VCardText class="d-flex flex-column justify-center">
          This is your Credential Token. Please save it.
          <VTextarea v-model="credentialToken" variant="outlined" readonly/>
          <VBtn @click="openEncapsulation" color="primary" class="my-2">Go to VP incapsulation</VBtn>
          <VBtn @click="credentialRequestDialog=false" color="primary" class="mt-2">Close</VBtn>
        </VCardText>
      </VCard>
    </VDialog>
    <VDialog
        v-model="presentationRequestDialog"
        width="80%"
        title="Encapsulate Credential"
        persistent
    >
      <VCard
          width="100%"
          min-height="500"
          prepend-icon="mdi-certificate"
      >
        <VCardText class="d-flex flex-column justify-center" v-if="!vpToken">
          <VTextarea label="VC Token" v-model="credentialToken" variant="outlined"/>
          <VTextField label="Subject DID" v-model="subjectDid"/>
          <VTextField label="ETH Private key (will not leave your device)" v-model="privateKey"/>
          <VBtn @click="createVP" color="primary" class="my-2">Encapsulate</VBtn>
        </VCardText>
        <VCardText v-if="vpToken">
          This is your Verifiable Presentation Token. Please store in a safe place.
          <VTextarea label="VP Token" v-model="vpToken" variant="outlined" readonly/>
        </VCardText>
      </VCard>
    </VDialog>
  </VContainer>
</template>

<script lang="ts" setup>
import type {VerifiablePresentation, VPPayload} from "@/types";
import {etc, signAsync, utils} from '@noble/secp256k1';
import {SignJWT} from 'jose';
import {type Ref, ref} from "vue";
import {useAppStore} from "@/stores/app.ts";

const appStore = useAppStore()

const credentialRequestDialog = ref(false)
const presentationRequestDialog = ref(false)
const credentialToken = ref('')
const privateKey = ref('')
const verificationId = ref('')
const vpToken = ref('')

const subjectRole = ref(undefined) as Ref<string | undefined>
const subjectDid = ref('') as Ref<string>
const subjectCompanyName = ref('') as Ref<string>
const subjectCompanyAddress = ref('') as Ref<string>
const subjectCompanyVat = ref('') as Ref<string>
const subjectCompanyWebsite = ref('') as Ref<string>
const subjectCompanyEmail = ref('') as Ref<string>
const subjectCompanyCountry = ref('') as Ref<string>
const subjectSpecialization = ref('') as Ref<string>
const subjectAccreditedBy = ref('') as Ref<string>
const subjectAuthorizedHosts = ref(['']) as Ref<string[]>

function openEncapsulation() {
  credentialRequestDialog.value = false
  presentationRequestDialog.value = true
}

function setRole(role: string) {
  subjectRole.value = role
}

async function requestCredential() {
  if (!subjectDid.value.trim()) {
    appStore.addToastMessage('Please enter your DID', 'error')
    return false
  }
  if (!subjectCompanyName.value.trim()) {
    appStore.addToastMessage('Please enter your company name', 'error')
    return false
  }
  if (!subjectCompanyAddress.value.trim()) {
    appStore.addToastMessage('Please enter your company address', 'error')
    return false
  }
  if (!subjectCompanyVat.value.trim()) {
    appStore.addToastMessage('Please enter your company VAT', 'error')
    return false
  }
  if (!subjectCompanyWebsite.value.trim()) {
    appStore.addToastMessage('Please enter your company website', 'error')
    return false
  }
  if (!subjectCompanyEmail.value.trim()) {
    appStore.addToastMessage('Please enter your company email', 'error')
    return false
  }
  if (!subjectCompanyCountry.value.trim()) {
    appStore.addToastMessage('Please enter your company country', 'error')
    return false
  }
  if (!subjectSpecialization.value.trim()) {
    appStore.addToastMessage('Please enter your specialization', 'error')
    return false
  }
  if (subjectRole.value == 'factChecker' && !subjectAccreditedBy.value.trim()) {
    appStore.addToastMessage('Please enter the accredited by company', 'error')
    return false
  }
  if (subjectRole.value == 'publisher' && subjectAuthorizedHosts.value.length === 0) {
    appStore.addToastMessage('Please enter the authorized hosts', 'error')
    return false
  }
  const credentialSubject = {
    subject_did: subjectDid.value,
    company_name: subjectCompanyName.value,
    company_address: subjectCompanyAddress.value,
    company_vat: subjectCompanyVat.value,
    company_website: subjectCompanyWebsite.value,
    company_email: subjectCompanyEmail.value,
    company_country: subjectCompanyCountry.value,
    specialization: subjectSpecialization.value,
    accredited_by: undefined as string | undefined,
    authorized_hosts: undefined as string[] | undefined,
  }
  if (subjectRole.value == 'factChecker')
    credentialSubject['accredited_by'] = subjectAccreditedBy.value
  if (subjectRole.value == 'publisher')
    credentialSubject['authorized_hosts'] = subjectAuthorizedHosts.value
  const response = await appStore.requestCredential(credentialSubject, subjectRole.value as string)
  if (response) {
    appStore.addToastMessage('Credentials approved!', 'success')
    credentialToken.value = response
    credentialRequestDialog.value = true
  } else {
    appStore.addToastMessage('Error sending credential request', 'error')
  }
}

function toBase64Url(bytes: Uint8Array): string {
  return btoa(String.fromCharCode(...bytes))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/g, '');
}

function bigintTo32Bytes(n: bigint): Uint8Array {
  return etc.hexToBytes(
      n.toString(16).padStart(64, '0')
  );
}

function getIssuerDidFromVcToken(vcToken: string): string {
  const [, payloadB64] = vcToken.split('.');
  const payload = JSON.parse(atob(payloadB64.replace(/-/g, '+').replace(/_/g, '/')));
  if (!payload.iss) throw new Error('vc_token JWT has no "iss" claim');
  return payload.iss;
}


function base64url(input: Uint8Array | string): string {
  const bytes =
      typeof input === 'string'
          ? new TextEncoder().encode(input)
          : input;

  return btoa(String.fromCodePoint(...bytes))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/g, '');
}

async function signES256KJWT(
    header: object,
    payload: object,
    privateKeyHex: string
) {
  const privateKey = etc.hexToBytes(
      privateKeyHex.replace(/^0x/i, '')
  );

  if (!utils.isValidSecretKey(privateKey)) {
    throw new Error('Invalid private key');
  }

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

  // Sign
  const signature = await signAsync(
      hash,
      privateKey,
      {
        der: false,
      }
  );

  const encodedSignature =
      base64url(signature);

  return `${signingInput}.${encodedSignature}`;
}

async function createVP() {
  if (!credentialToken.value.trim()) {
    appStore.addToastMessage('Please enter the credential token', 'error')
    return false
  }
  if (!subjectDid.value.trim()) {
    appStore.addToastMessage('Please enter your DID', 'error')
    return false
  }
  if (!privateKey.value.trim()) {
    appStore.addToastMessage('Please enter your private key', 'error')
    return false
  }

  const aud = getIssuerDidFromVcToken(credentialToken.value)
  if (!aud) {
    appStore.addToastMessage('Invalid credential token', 'error')
    return false
  }

  const urnStr = `urn:uuid:${crypto.randomUUID()}`;
  const now = Math.floor(Date.now() / 1000);

  const vp: VerifiablePresentation = {
    '@context': ['https://www.w3.org/2018/credentials/v1'],
    id: urnStr,
    type: ['VerifiablePresentation'],
    holder: subjectDid.value,
    verifiableCredential: credentialToken.value ? [credentialToken.value] : [],
  };

  const payload: VPPayload = {
    iss: subjectDid.value,
    aud: aud,
    sub: subjectDid.value,
    iat: now,
    nbf: now,
    exp: now + 10 * 365 * 24 * 60 * 60,
    nonce: urnStr,
    jti: urnStr,
    vp: vp,
  };

  const privateKeyHex = privateKey.value.replace(/^0x/i, '');

  const headers: { typ: string, alg: string, kid?: string } = {typ: 'JWT', alg: 'ES256K'};
  if (verificationId.value) headers['kid'] = verificationId.value;

  const jwt = await signES256KJWT(
      headers,
      payload,
      privateKeyHex
  );

  vpToken.value = jwt

}
</script>

<style scoped>
</style>
