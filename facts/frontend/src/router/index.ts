import {createRouter, createWebHistory} from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            component: () => import('@/pages/HomeView.vue'),
        },
        {
            path: '/login',
            name: 'login',
            component: () => import('@/pages/LoginView.vue'),
        },
        {
            path: '/articles',
            name: 'articles',
            component: () => import('@/pages/ArticleListView.vue'),
        },
        {
            path: '/articles/:id',
            name: 'article',
            component: () => import('@/pages/ArticleView.vue'),
        },
        {
            path: '/articles/submit',
            component: () => import('@/pages/CreateArticleView.vue'),
            meta: {public: false}
        },
        {
            path: '/assessments',
            name: 'assessments',
            component: () => import('@/pages/AssessmentListView.vue'),
        },
        {
            path: '/assessments/submit',
            component: () => import('@/pages/CreateAssessmentView.vue'),
            meta: {public: false}
        },
        {
            path: '/onboarding',
            component: () => import('../pages/IssuerView.vue'),
            meta: {public: false}
        },
        {
            path: '/wallet',
            component: () => import('../pages/WalletView.vue'),
            meta: {public: false}
        }
    ],
})
export default router
