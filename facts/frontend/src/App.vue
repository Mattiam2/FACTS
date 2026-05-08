<template>
  <VApp>
    <AppLayout>
      <RouterView/>
      <VSnackbarQueue
          v-model="toastMessages"
          :total-visible="5"
          :timeout="1000"
          closable
      />
    </AppLayout>
  </VApp>
</template>

<script lang="ts" setup>
  import {storeToRefs} from "pinia";
  import AppLayout from "@/layouts/AppLayout.vue";
  import {useAppStore} from "@/stores/app.ts";

  const appStore = useAppStore()
  const {toastMessages} = storeToRefs(appStore)
</script>
