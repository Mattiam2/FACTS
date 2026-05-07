import vuetify from 'eslint-config-vuetify'

export default vuetify({
        vue: true,
        ts: true,
        stylistic: false,
    },
    {
        rules: {
            'vue/attributes-order': 'off',
            'vue/html-indent': 'off',
            'vue/padding-line-between-tags': 'off',
            'vue/max-attributes-per-line': 'off',
            'vue/html-closing-bracket-spacing': 'off',
            'vue/script-indent': 'off',
            'vue/first-attribute-linebreak': 'off',
            '@stylistic/indent': 'off',
        },
    })
