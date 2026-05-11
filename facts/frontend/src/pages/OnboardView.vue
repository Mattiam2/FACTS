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
            What is your role?<br>
            <VBtn prepend-icon="mdi-newspaper" class="me-2" color="secondary" @click="subjectRole='publisher'">I am a
              Publisher
            </VBtn>
            <VBtn prepend-icon="mdi-head-check" class="ms-2" color="secondary" @click="subjectRole='factChecker'">I am a
              Fact Checker
            </VBtn>
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
          <VBtn @click="credentialRequestDialog=false" color="primary" class="my-2">Go to VP incapsulation</VBtn>
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
        <VCardText class="d-flex flex-column justify-center">
          <VTextarea label="VC Token" v-model="credentialToken" variant="outlined"/>
          <VTextField label="Subject DID" v-model="subjectDid"/>
          <VTextField label="ETH Private key (will not be stored)" v-model="privateKey"/>
          <VBtn @click="createVP" color="primary" class="my-2">Encapsulate</VBtn>/
        </VCardText>
      </VCard>
    </VDialog>
  </VContainer>
</template>

<script lang="ts" setup>
import {type Ref, ref} from "vue";
import {useAppStore} from "@/stores/app.ts";

const appStore = useAppStore()

const credentialRequestDialog = ref(false)
const presentationRequestDialog = ref(false)
const credentialToken = ref('')
const privateKey = ref('')

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
  
}
</script>

<style scoped>
</style>
