<template>
  <AppHeader />

  <div class="main-content">
    <router-view />
  </div>

  <AppFooter />

  <!-- Password Prompt for unlocking encrypted changes -->
  <PasswordPrompt
    v-if="showPasswordPrompt"
    @unlocked="onUnlocked"
    @skipped="onSkipped"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue';
import AppHeader from './components/AppHeader.vue';
import AppFooter from './components/AppFooter.vue';
import PasswordPrompt from './components/PasswordPrompt.vue';
import { useAuthStore } from './stores/auth';
import { useBankStore } from './stores/bank';

const showPasswordPrompt = ref(false);

// Check for existing login session on app load
const authStore = useAuthStore();
const bankStore = useBankStore();

onMounted(() => {
  authStore.checkAuth();

  // Show password prompt if user is logged in and has encrypted data
  if (authStore.isLoggedIn && bankStore.hasEncryptedData()) {
    showPasswordPrompt.value = true;
  }
});

function onUnlocked() {
  showPasswordPrompt.value = false;
}

function onSkipped() {
  showPasswordPrompt.value = false;
  // User chose to skip, they can continue with empty state
}
</script>