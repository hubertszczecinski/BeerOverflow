<template>
  <nav class="navbar navbar-expand-lg top-navbar" role="navigation" aria-label="Utility">
    <div class="container">
      <router-link class="navbar-brand" to="/">
        <strong>BeerBank</strong>
      </router-link>
      <div class="search-login ms-auto">
        <template v-if="authStore.isLoggedIn">
          <router-link to="/dashboard" class="login-btn">
            <i class="fas fa-user-circle" aria-hidden="true"></i> My Account
          </router-link>
          <a @click.prevent="authStore.logout()" href="#" class="login-btn">
            <i class="fas fa-sign-out-alt" aria-hidden="true"></i> Log Out
          </a>
        </template>
        <template v-else>
          <router-link to="/login" class="login-btn">
            <i class="fas fa-sign-in-alt" aria-hidden="true"></i> Login
          </router-link>
        </template>

      </div>
    </div>
  </nav>

  <nav class="navbar navbar-expand-lg main-navbar navbar-dark" role="navigation" aria-label="Primary">
    <div class="container-fluid px-0">
      <!-- Mobile Toggler -->
      <button class="navbar-toggler ms-2" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav" aria-controls="mainNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <!-- Collapsible Menu -->
      <div id="mainNav" class="collapse navbar-collapse">
        <ul class="navbar-nav w-100">
          <li class="nav-item">
            <router-link class="nav-link" to="/accounts">
              <i class="fas fa-credit-card d-block mb-1" aria-hidden="true"></i>
              Accounts & Cards
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/savings">
              <i class="fas fa-piggy-bank d-block mb-1" aria-hidden="true"></i>
              Savings & Investments
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/credit">
              <i class="fas fa-hand-holding-usd d-block mb-1" aria-hidden="true"></i>
              Loans & Financing
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/securities">
              <i class="fas fa-chart-line d-block mb-1" aria-hidden="true"></i>
              Securities Trading
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/insurance">
              <i class="fas fa-shield-alt d-block mb-1" aria-hidden="true"></i>
              Insurance
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/magazine">
              <i class="fas fa-newspaper d-block mb-1" aria-hidden="true"></i>
              Magazine
            </router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();
</script>