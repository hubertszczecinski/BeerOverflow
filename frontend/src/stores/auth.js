import { defineStore } from 'pinia';
import router from '@/router';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null, // This will hold user info (username, email, etc.)
    }),
    getters: {
        isLoggedIn: (state) => !!state.user,
    },
    actions: {
        async login(credentials) {
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(credentials),
                });

                if (!response.ok) {
                    throw new Error('Login failed');
                }

                const data = await response.json();
                this.user = data.user; // Assuming API returns { user: {...} }

                // Persist login (e.g., in localStorage)
                localStorage.setItem('user', JSON.stringify(data.user));

                router.push('/dashboard');
            } catch (error) {
                console.error(error);
                // Here you would dispatch to an alert store
                alert('Invalid username or password');
            }
        },

        async register(formData) {
            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    body: formData, // FormData is sent directly, no Content-Type header
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || 'Registration failed');
                }

                // On success, redirect to login
                router.push('/login');
                alert('Registration successful! Please log in.');

            } catch (error) {
                console.error(error);
                alert(error.message);
            }
        },

        logout() {
            this.user = null;
            localStorage.removeItem('user');
            router.push('/login');
        },

        // Call this on app load to check for persisted session
        checkAuth() {
            const user = localStorage.getItem('user');
            if (user) {
                this.user = JSON.parse(user);
            }
        }
    },
});