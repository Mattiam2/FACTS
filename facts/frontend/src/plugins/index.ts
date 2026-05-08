// Types
import type { App } from 'vue'
import {createPinia} from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import router from '../router';
import i18n from './i18n';
// Plugins
import vuetify from './vuetify'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

export function registerPlugins (app: App) {
 app.use(vuetify)
 app.use(pinia);
 app.use(i18n);
 app.use(router);
}