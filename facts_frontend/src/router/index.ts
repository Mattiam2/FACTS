import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from "@/stores/auth.ts";

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
            meta: {public: false, role: 'publisher'}
        },
        {
            path: '/assessments',
            name: 'assessments',
            component: () => import('@/pages/AssessmentListView.vue'),
        },
        {
            path: '/assessments/submit',
            component: () => import('@/pages/CreateAssessmentView.vue'),
            meta: {public: false, role: 'factChecker'}
        },
        {
            path: '/onboarding',
            component: () => import('../pages/IssuerView.vue'),
        },
        {
            path: '/wallet',
            component: () => import('../pages/WalletView.vue'),
        }
    ],
})


router.beforeEach(async (to, from) => {
    const authStore = useAuthStore()
    if (
        to.meta?.public !== undefined && !to.meta.public
        && (!authStore.factsAccessToken || (to.meta.role && authStore.factsCredentialSubject?.role != to.meta.role))) {
        return {path: '/login'}
    }
})
export default router
