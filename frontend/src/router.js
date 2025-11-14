// src/router.js
import { createRouter, createWebHistory } from 'vue-router'
// Home page component (rendered inside App.vue's <RouterView />)
const HomePage = () => import('./components/HomePage.vue')

// Import your page components (we'll create these next)
const AuthenticatePage = () => import('./views/FaceAuthView.vue')
const TransferPage = () => import('./components/TransferPage.vue')

const routes = [
    {
        path: '/',
        name: 'Home',
        component: HomePage
    },
    {
        path: '/authenticate',
        name: 'Authenticate',
        component: AuthenticatePage
    },
    {
        path: '/transfer',
        name: 'Transfer',
        component: TransferPage
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router