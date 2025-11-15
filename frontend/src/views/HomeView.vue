<template>
  <div class="hero-banner">
    <div class="container">
      <h1>The Bank by Your Side</h1>
      <p>Modern banking solutions for you</p>

      <template v-if="!authStore.isLoggedIn">
        <router-link to="/register" class="btn btn-primary btn-lg me-3" style="border: 1px solid #000;">
          <i class="fas fa-user-plus"></i> Open Account
        </router-link>
        <router-link to="/login" class="btn btn-outline-primary btn-lg" style="color:black; border: 1px solid #000;">
          <i class="fas fa-sign-in-alt"></i> Login
        </router-link>
      </template>
      <template v-else>
        <router-link to="/dashboard" class="btn btn-primary btn-lg">
          <i class="fas fa-home"></i> Go to Dashboard
        </router-link>
      </template>

    </div>
    <!-- Voice Navigation (floating button) -->
    <VoiceNavBox />
  </div>

</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import VoiceNavBox from '@/components/VoiceNavBox.vue';
const authStore = useAuthStore();
</script>

