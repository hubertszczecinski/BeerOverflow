// src/router.js
import { createRouter, createWebHistory } from 'vue-router'
import Home from './App.vue' // Your main app component

// Import your page components (we'll create these next)
const AuthenticatePage = () => import('./components/FaceAuthPage.vue')
const TransferPage = () => import('./components/TransferPage.vue')

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home
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