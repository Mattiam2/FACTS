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
                <VBtn @click="openEncapsulation" color="primary" class="ma-1" v-if="!authStore.factsAccessToken">Create
                  Verifiable Presentation
                </VBtn>
                <VBtn @click="openOnboardingEbsi" color="primary" class="ma-1" v-if="!authStore.factsAccessToken">
                  Onboard on EBSI DID Register
                </VBtn>
                <VBtn @click="openVerificationMethodCreation" color="primary" class="ma-1"
                      v-if="!authStore.factsAccessToken">
                  Add Verification Method
                </VBtn>
                <VBtn @click="openAuthoriseDid" color="primary" class="ma-1" v-if="!authStore.factsAccessToken">
                  Onboard on EBSI Track and Trace
                </VBtn>
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
        <VCardText class="d-flex flex-column justify-center" v-if="!stepOneVpToken">
          <VTextarea label="VC Token" v-model="credentialToken" class="h-100" variant="outlined"/>
          <VTextField label="Verification ID" v-model="verificationId"/>
          <VTextField label="Private key (will not leave your device)" placeholder="0x..." v-model="privateKey"/>
          <VRadioGroup label="Algorithm:" v-model="algorithmType">
            <VRadio label="ES256" value="ES256"/>
            <VRadio label="ES256K" value="ES256K"/>
          </VRadioGroup>
          <VBtn @click="createVP" color="primary" class="my-2">Encapsulate</VBtn>
        </VCardText>
        <VCardText v-if="stepOneVpToken" class="d-flex flex-column">
          This is your Verifiable Presentation Token. Please store in a safe place.
          <VTextarea label="VP Token" v-model="stepOneVpToken" variant="outlined" class="mt-5" readonly/>
          <VBtn color="primary" @click="presentationRequestDialog = false">Close</VBtn>
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
                    :items="['Provide VP', 'Get DIDR Invite', 'Insert DID Document']">
            <template #item.1>
              <VSheet min-height="300">
                Please present a valid VerifiableAuthorisationToOnboard issued by Root TAO or TAO
                <VTextarea label="VP Token" v-model="stepOneVpToken" class="mt-5" variant="outlined"/>
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
                <VTextField label="Verification Method ID" v-model="stepThreeVMethodId"/>
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


    <VDialog
        v-model="addVerificationMethodDialog"
        width="80%"
        title="Add Verification Method"
    >
      <VCard
          width="100%"
          min-height="500"
          prepend-icon="mdi-certificate"
      >
        <VCardText>
          <VStepper v-model="addVMethodStep" :flat="true" elevation="0"
                    :items="['Provide VP', 'Get DIDR Write', 'Add Verification Method', 'Done']">
            <template #item.1>
              <VSheet min-height="300">
                Please present a signed Verifiable Presentation onboarded on DID Registry
                <VTextarea label="VP Token" v-model="stepOneVpToken" class="mt-5" variant="outlined"/>
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
                <VTextField label="Verification Method ID" v-model="stepThreeVMethodId"/>
                <VTextField label="Public Key" placeholder="0x..." v-model="stepThreePublicKey"/>
                <VCard subtitle="Relationship" variant="tonal" class="my-2">
                  <VCardText>
                    <VCheckbox
                        v-model="stepThreeVMethodRels"
                        label="Authentication"
                        value="authentication"
                        hide-details
                        density="compact"
                    />
                    <VCheckbox
                        v-model="stepThreeVMethodRels"
                        label="Assertion Method"
                        value="assertionMethod"
                        hide-details
                        density="compact"
                    />
                    <VCheckbox
                        v-model="stepThreeVMethodRels"
                        label="Capability Invocation"
                        value="capabilityInvocation"
                        hide-details
                        density="compact"
                    />
                    <VCheckbox
                        v-model="stepThreeVMethodRels"
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
                <div v-else-if="txHash">
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

    <VDialog
        v-model="tntAuthoriseDialog"
        width="80%"
        title="Get whitelisted on Track and Trace"
    >
      <VCard
          width="100%"
          min-height="500"
          prepend-icon="mdi-certificate"
      >
        <VCardText>
          <VStepper v-model="tntAuthoriseStep" :flat="true" elevation="0"
                    :items="['Provide VP', 'Get TNT Authorise', 'Sign transaction']">
            <template #item.1>
              <VSheet min-height="300">
                Please present a signed Verifiable Presentation onboarded on DID Registry
                <VTextarea label="VP Token" v-model="stepOneVpToken" class="mt-5" variant="outlined"/>
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
                <div v-if="!transactionToSign">
                  <VProgressCircular indeterminate/>
                  Requesting transaction...
                </div>
                <div v-else-if="!txHash">
                  <VBtn @click="signTntTransaction">Sign transaction</VBtn>
                </div>
                <div v-else-if="txHash">
                  DID is now whitelisted on TNT!
                </div>
              </VSheet>
            </template>
            <template #actions="{ prev, next }">
              <VStepperActions
                  @click:next="tntAuthoriseCustomNext(next)"
                  :disabled="(tntAuthoriseStep === 2 && !walletStore.ebsiAccessToken)"
                  @click:prev="prev"/>
            </template>
          </VStepper>
        </VCardText>
      </VCard>
    </VDialog>
  </VContainer>
</template>

<script lang="ts" setup>
import type {FactsSubjectCredential, VerifiablePresentation, VPPayload} from "@/types";
import {hexToBytes} from '@noble/curves/abstract/utils'
import {p256} from '@noble/curves/p256';
import {secp256k1} from '@noble/curves/secp256k1'
import {type Ref, ref} from "vue";
import {useAppStore} from "@/stores/app.ts";
import {useAuthStore} from "@/stores/auth.ts";
import {useWalletStore} from "@/stores/wallet.ts";
import {extractSubjectCredential} from "@/utility.ts";

const appStore = useAppStore()
const walletStore = useWalletStore()
const authStore = useAuthStore()

const loadingText = ref('Loading...')
const onboardingStep = ref(1) as Ref<number>
const addVMethodStep = ref(1) as Ref<number>
const tntAuthoriseStep = ref(1) as Ref<number>
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
const addVerificationMethodDialog = ref(false)
const tntAuthoriseDialog = ref(false)
const credentialToken = ref('')
const privateKey = ref('')
const verificationId = ref('')
const stepOneVpToken = ref('')
const subjectCredential = ref(undefined) as Ref<FactsSubjectCredential | undefined>
const stepThreeVMethodId = ref('')
const stepThreeVMethodRels = ref<string[]>([])
const stepThreePublicKey = ref('')
const transactionToSign = ref(undefined) as Ref<object | undefined>
const txHash = ref('') as Ref<string>
const addVMethodCompleted = ref(false)

const algorithmType = ref('ES256') as Ref<string>

function openEncapsulation() {
  walletStore.ebsiAccessToken = undefined
  presentationRequestDialog.value = true
}

function openOnboardingEbsi() {
  walletStore.ebsiAccessToken = undefined
  onboardingEbsiDialog.value = true
}

function openVerificationMethodCreation() {
  walletStore.ebsiAccessToken = undefined
  addVerificationMethodDialog.value = true
}

function openAuthoriseDid() {
  walletStore.ebsiAccessToken = undefined
  tntAuthoriseDialog.value = true
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

async function onboardingCustomNext(next: () => void) {
  if (onboardingStep.value == 1) {
    if (!stepOneVpToken.value.trim()) {
      appStore.addToastMessage('Please enter the VP token', 'error')
      return false
    }
    const parts = stepOneVpToken.value.split('.')
    if (parts.length !== 3) {
      appStore.addToastMessage('Invalid JWT format', 'error')
      stepOneVpToken.value = ''
      return false
    }
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
    stepThreeVMethodId.value = JSON.parse(atob(parts[0]))['kid'].split('#')[1]
    subjectCredential.value = extractSubjectCredential(payload.vp.verifiableCredential[0])
    walletStore.requestEbsiAccessToken(stepOneVpToken.value, "didr_invite")
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
    walletStore.createDidDocumentTransaction(subjectCredential.value, stepThreeVMethodId.value).then(response => {
      transactionToSign.value = response.result
    })
    next()
  }
}

async function addVMethodCustomNext(next: () => void) {
  if (addVMethodStep.value == 1) {
    if (!stepOneVpToken.value.trim()) {
      appStore.addToastMessage('Please enter the VP token', 'error')
      return false
    }
    const parts = stepOneVpToken.value.split('.')
    if (parts.length !== 3) {
      appStore.addToastMessage('Invalid JWT format', 'error')
      stepOneVpToken.value = ''
      return false
    }
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
    stepThreeVMethodId.value = JSON.parse(atob(parts[0]))['kid'].split('#')[1]
    subjectCredential.value = extractSubjectCredential(payload.vp.verifiableCredential[0])
    walletStore.requestEbsiAccessToken(stepOneVpToken.value, "didr_write")
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
    walletStore.createDidDocumentTransaction(subjectCredential.value, stepThreeVMethodId.value).then(response => {
      transactionToSign.value = response.result
    })
    next()
  } else if (addVMethodStep.value == 3) {
    if (!subjectCredential.value) {
      appStore.addToastMessage("You've skipped step One!", 'error')
      return false
    }
    if (!stepThreeVMethodId.value.trim()) {
      appStore.addToastMessage('Please enter the verification method ID', 'error')
      return false
    }
    if (!stepThreePublicKey.value.trim()) {
      appStore.addToastMessage('Please enter the verification method public key', 'error')
      return false
    }
    if (stepThreeVMethodRels.value.length === 0) {
      appStore.addToastMessage('Please select at least one relationship', 'error')
      return false
    }
    next()
    loadingText.value = 'Creating addVerificationMethod transaction...'
    const response = await walletStore.createVerificationMethodTransaction(subjectCredential.value, stepThreeVMethodId.value, stepThreePublicKey.value, algorithmType.value == "ES256K")
    transactionToSign.value = response.result
    loadingText.value = 'Signing addVerificationMethod transaction...'
    const vMethodAddedResult = await signDidrTransaction()
    loadingText.value = 'Verification method added!'
    if(vMethodAddedResult) {
      for(const rel of stepThreeVMethodRels.value) {
        loadingText.value = `Creating addVerificationRelationship transaction for ${rel}...`
        const response = await walletStore.createVerificationRelationshipTransaction(subjectCredential.value, stepThreeVMethodId.value, rel)
        transactionToSign.value = response.result
        loadingText.value = `Signing addVerificationRelationship transaction for ${rel}...`
        const result = await signDidrTransaction()
        if(!result){
          loadingText.value = `Error signing addVerificationRelationship transaction for ${rel}!`
          return
        }
        loadingText.value = `Verification relationship ${rel} added!`
      }
      addVMethodCompleted.value = true
    }
  }
}

async function tntAuthoriseCustomNext(next: () => void) {
  if (tntAuthoriseStep.value == 1) {
    if (!stepOneVpToken.value.trim()) {
      appStore.addToastMessage('Please enter the VP token', 'error')
      return false
    }
    const parts = stepOneVpToken.value.split('.')
    if (parts.length !== 3) {
      appStore.addToastMessage('Invalid JWT format', 'error')
      stepOneVpToken.value = ''
      return false
    }
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
    subjectCredential.value = extractSubjectCredential(payload.vp.verifiableCredential[0])
    walletStore.requestEbsiAccessToken(stepOneVpToken.value, "tnt_authorise")
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
    walletStore.createAuthoriseDidTransaction(subjectCredential.value).then(response => {
      transactionToSign.value = response.result
    })
    next()
  }
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

async function signTntTransaction() {
  if (!transactionToSign.value) {
    appStore.addToastMessage('No transaction to sign', 'error')
    return false
  }
  const signedTransaction = await walletStore.signTransaction(transactionToSign.value)
  const response = await walletStore.confirmTntTransaction(signedTransaction)
  txHash.value = response.result
  return response.result
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

  stepOneVpToken.value = await signJwt(
      headers,
      payload,
      privateKeyHex
  )

}
</script>

<style scoped>
</style>
