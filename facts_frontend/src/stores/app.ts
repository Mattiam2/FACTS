import {defineStore} from 'pinia'

export const useAppStore = defineStore('app', {
    state: () => ({
        toastMessages: [] as { text: string, color?: string, onDismiss?: () => void }[]
    }),
    actions: {
        addToastMessage(text: string, type: 'success' | 'error' = 'success') {
            this.toastMessages.push({text, color: type})
        }
    },
    persist: false,
})
