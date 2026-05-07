import { createRouter, createWebHistory } from 'vue-router'
import ArticleView from '@/pages/ArticleView.vue'
import LoginView from '@/pages/LoginView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            redirect: '/login'
        },
        {
            path: '/login',
            name: 'login',
            component: LoginView,
        },
        {path: '/articles/submit', component: ArticleView, meta: {public: false}}
    ],
})
export default router
