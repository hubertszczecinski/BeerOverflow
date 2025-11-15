import { defineStore } from 'pinia';
import router from '@/router';
import { useBankStore } from './bank';

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
                    credentials: 'include', // Important for session cookies
                });

                if (!response.ok) {
                    throw new Error('Login failed');
                }
                const ct = response.headers.get('content-type') || '';
                if (!ct.includes('application/json')) {
                    const txt = await response.text();
                    throw new Error(`Unexpected non-JSON response: ${txt.slice(0,120)}`);
                }
                const data = await response.json();
                this.user = data.user; // Assuming API returns { user: {...} }

                // Persist login (e.g., in localStorage)
                localStorage.setItem('user', JSON.stringify(data.user));

                // Initialize bank store with the password
                const bankStore = useBankStore();
                try {
                    await bankStore.initializeSession(credentials.password);
                } catch (err) {
                    console.error('Failed to initialize bank store:', err);
                    // Don't fail login if bank store initialization fails
                }

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
                    credentials: 'include', // Important for session cookies
                });

                if (!response.ok) {
                    let message = 'Registration failed';
                    try {
                        const ct = response.headers.get('content-type') || '';
                        if (ct.includes('application/json')) {
                            const errorData = await response.json();
                            message = errorData.message || message;
                        } else {
                            message = (await response.text()).slice(0,200) || message;
                        }
                    } catch {}
                    throw new Error(message);
                }

                // On success, redirect to login
                router.push('/login');
                alert('Registration successful! Please log in.');

            } catch (error) {
                console.error(error);
                alert(error.message);
            }
        },

        async logout() {
            try {
                await fetch('/api/logout', {
                    method: 'POST',
                    credentials: 'include',
                });
            } catch (error) {
                console.error('Logout error:', error);
            } finally {
                // Clear local state regardless of API response
                this.user = null;
                localStorage.removeItem('user');
                router.push('/login');
            }
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
