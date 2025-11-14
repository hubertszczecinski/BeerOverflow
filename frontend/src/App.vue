<template>
  <AppHeader />

  <div class="main-content">
    <router-view />
  </div>

  <AppFooter />
</template>

<script setup>
import { onMounted } from 'vue';
import AppHeader from './components/AppHeader.vue';
import AppFooter from './components/AppFooter.vue';
import { useAuthStore } from './stores/auth';

// Check for existing login session on app load
const authStore = useAuthStore();
onMounted(() => {
  authStore.checkAuth();
});
</script>