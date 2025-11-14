<template>
  <nav class="navbar navbar-expand-lg top-navbar">
    <div class="container">
      <router-link class="navbar-brand" to="/">
        <strong>Commerzbank</strong>
      </router-link>
      <div class="search-login ms-auto">
        <a href="#" class="search-icon">
          <i class="fas fa-search"></i>
        </a>

        <template v-if="authStore.isLoggedIn">
          <router-link to="/dashboard" class="login-btn">
            <i class="fas fa-user-circle"></i> My Account
          </router-link>
          <a @click.prevent="authStore.logout()" href="#" class="login-btn">
            <i class="fas fa-sign-out-alt"></i> Log Out
          </a>
        </template>
        <template v-else>
          <router-link to="/login" class="login-btn">
            <i class="fas fa-sign-in-alt"></i> Login
          </router-link>
        </template>

      </div>
    </div>
  </nav>

  <nav class="navbar navbar-expand-lg main-navbar navbar-dark">
    <div class="container-fluid px-0">
      <ul class="navbar-nav w-100">
        <li class="nav-item">
          <router-link class="nav-link" to="/accounts">
            <i class="fas fa-credit-card d-block mb-1"></i>
            Accounts & Cards
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/savings">
            <i class="fas fa-piggy-bank d-block mb-1"></i>
            Savings & Investments
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/credit">
            <i class="fas fa-hand-holding-usd d-block mb-1"></i>
            Loans & Financing
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/securities">
            <i class="fas fa-chart-line d-block mb-1"></i>
            Securities Trading
            </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/insurance">
            <i class="fas fa-shield-alt d-block mb-1"></i>
            Insurance
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/magazine">
            <i class="fas fa-newspaper d-block mb-1"></i>
            Magazine
          </router-link>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();
</script>