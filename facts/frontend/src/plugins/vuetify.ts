/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Composables
import {createVuetify} from 'vuetify'
import {md3} from 'vuetify/blueprints'
import {VDateInput} from 'vuetify/labs/VDateInput'
// Styles
import '@mdi/font/css/materialdesignicons.css'
import '../styles/layers.css'
import 'vuetify/styles'


// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
    components: {
        VDateInput,
    },
    theme: {
        defaultTheme: 'facts',
        themes: {
            facts: {
                dark: true,
                colors: {
                    background: '#080d1a',
                    surface: '#0f1629',
                    primary: '#00e5b4',
                    'primary-darken-1': '#00b890',
                    secondary: '#4a6cf7',
                    error: '#ff5252',
                    warning: '#ffb300',
                    success: '#00e5b4',
                    'on-background': '#e8eaf0',
                    'on-surface': '#e8eaf0',
                    'on-primary': '#080d1a',
                },
            },
        },
    }
})
