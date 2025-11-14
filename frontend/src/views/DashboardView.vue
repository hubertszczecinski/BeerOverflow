<template>
  <div class="container">
    <div class="row">
      <div class="col-12">
        <div class="dashboard-card">
          <h2>Welcome, {{ authStore.user?.first_name || authStore.user?.username }}!</h2>
          <p class="mb-0">Manage Your Bank Account</p>
        </div>
      </div>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-md-3">
        <div class="product-card text-center">
          <div class="card-icon"><i class="fas fa-exchange-alt"></i></div>
          <h4>Transfer</h4>
          <a href="#" class="btn btn-primary btn-sm w-100">Transfer Now</a>
        </div>
      </div>
    </div>

    <div class="row" v-if="authStore.user">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Account Information</h5>
          </div>
          <div class="card-body">
            <table class="table">
              <tbody>
              <tr>
                <th style="width: 200px;">Username:</th>
                <td>{{ authStore.user.username }}</td>
              </tr>
              <tr>
                <th>Email:</th>
                <td>{{ authStore.user.email }}</td>
              </tr>
              <tr>
                <th>Name:</th>
                <td>{{ authStore.user.first_name }} {{ authStore.user.last_name }}</td>
              </tr>
              <tr>
                <th>Member Since:</th>
                <td>{{ formatDate(authStore.user.created_at) }}</td>
              </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Account Balance</h5>
          </div>
          <div class="card-body text-center">
            <h2 class="text-primary mb-3">10,000.00 €</h2>
            <p class="text-muted">Current Account</p>
            <a href="#" class="btn btn-outline-primary w-100">View Details</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  // Replicates the 'dd.mm.yyyy' format
  return new Date(dateString).toLocaleDateString('de-DE');
};
</script>