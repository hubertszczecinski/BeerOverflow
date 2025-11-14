<template>
  <div class="container">
    <div class="login-container">
      <div class="card">
        <div class="card-header text-center">
          <h3>Login</h3>
        </div>
        <div class="card-body">
          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label for="username" class="form-label">Username</label>
              <input type="text" class="form-control" id="username" v.model="username" required>
            </div>

            <div class="mb-3">
              <label for="password" class="form-label">Password</label>
              <input type="password" class="form-control" id="password" v-model="password" required>
            </div>

            <div class="mb-3 form-check">
              <input type="checkbox" class="form-check-input" id="remember_me" v-model="rememberMe">
              <label class="form-check-label" for="remember_me">Remember me</label>
            </div>

            <div class="d-grid">
              <button type="submit" class="btn btn-primary">Log In</button>
            </div>
          </form>

          <hr>

          <div class="text-center">
            <p>Don't have an account? <router-link to="/register">Register</router-link></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

const username = ref('');
const password = ref('');
const rememberMe = ref(false);
const authStore = useAuthStore();

const handleLogin = () => {
  authStore.login({
    username: username.value,
    password: password.value,
  });
};
</script>