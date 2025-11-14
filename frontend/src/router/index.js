import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import DashboardView from '../views/DashboardView.vue';

import AccountsView from '../views/AccountsView.vue';
import SavingsView from '../views/SavingsView.vue';
import CreditView from '../views/CreditView.vue';
import SecuritiesView from '../views/SecuritiesView.vue';
import InsuranceView from '../views/InsuranceView.vue';
import MagazineView from '../views/MagazineView.vue';

const routes = [
    {
        path: '/',
        name: 'Home',
        component: HomeView,
    },
    {
        path: '/login',
        name: 'Login',
        component: LoginView,
    },
    {
        path: '/register',
        name: 'Register',
        component: RegisterView,
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: DashboardView,
        meta: { requiresAuth: true }, // Add meta field for protected routes
    },

    {
        path: '/accounts',
        name: 'Accounts',
        component: AccountsView,
    },
    {
        path: '/savings',
        name: 'Savings',
        component: SavingsView,
    },
    {
        path: '/credit',
        name: 'Credit',
        component: CreditView,
    },
    {
        path: '/securities',
        name: 'Securities',
        component: SecuritiesView,
    },
    {
        path: '/insurance',
        name: 'Insurance',
        component: InsuranceView,
    },
    {
        path: '/magazine',
        name: 'Magazine',
        component: MagazineView,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
    // This mimics the anchor link behavior (e.g., /#accounts)
    scrollBehavior(to, from, savedPosition) {
        if (to.hash) {
            return {
                el: to.hash,
                behavior: 'smooth',
            };
        }
        return { top: 0 };
    },
});

// Navigation Guard
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();

    if (to.meta.requiresAuth && !authStore.isLoggedIn) {
        // If route requires auth and user is not logged in, redirect to login
        next('/login');
    } else {
        // Otherwise, proceed
        next();
    }
});

export default router;