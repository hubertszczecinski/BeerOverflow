d<template>
  <div class="create-account-form">
    <form @submit.prevent="handleSubmit">
      <div class="mb-3">
        <label for="accountType" class="form-label">Account Type</label>
        <select
          id="accountType"
          v-model="formData.accountType"
          class="form-select"
          required
        >
          <option value="">Select account type...</option>
          <option value="checking">Checking Account</option>
          <option value="savings">Savings Account</option>
          <option value="business">Business Account</option>
          <option value="investment">Investment Account</option>
        </select>
        <div class="form-text">Choose the type of account you want to create</div>
      </div>

      <div class="mb-3">
        <label for="currency" class="form-label">Currency</label>
        <select
          id="currency"
          v-model="formData.currency"
          class="form-select"
          required
        >
          <option value="USD">USD - US Dollar</option>
          <option value="EUR">EUR - Euro</option>
          <option value="GBP">GBP - British Pound</option>
          <option value="JPY">JPY - Japanese Yen</option>
          <option value="CHF">CHF - Swiss Franc</option>
        </select>
        <div class="form-text">Select the currency for this account</div>
      </div>

      <div class="mb-3">
        <label for="initialBalance" class="form-label">Initial Balance (Optional)</label>
        <div class="input-group">
          <span class="input-group-text">{{ getCurrencySymbol(formData.currency) }}</span>
          <input
            type="number"
            id="initialBalance"
            v-model.number="formData.initialBalance"
            class="form-control"
            min="0"
            step="0.01"
            placeholder="0.00"
          >
        </div>
        <div class="form-text">You can start with a balance or leave it at 0</div>
      </div>

      <div class="mb-3">
        <label for="description" class="form-label">Description (Optional)</label>
        <textarea
          id="description"
          v-model="formData.description"
          class="form-control"
          rows="2"
          placeholder="e.g., Emergency fund, Business expenses..."
        ></textarea>
      </div>

      <div v-if="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
      </div>

      <div v-if="success" class="alert alert-success">
        <i class="bi bi-check-circle me-2"></i>
        {{ success }}
      </div>

      <div class="d-grid gap-2">
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="isSubmitting"
        >
          <span v-if="isSubmitting">
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Creating Account...
          </span>
          <span v-else>
            <i class="bi bi-plus-circle me-2"></i>
            Create Account
          </span>
        </button>
      </div>
    </form>

    <!-- Preview Card -->
    <div v-if="formData.accountType" class="card mt-4 bg-light">
      <div class="card-body">
        <h6 class="card-title">
          <i class="bi bi-eye me-2"></i>
          Preview
        </h6>
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <div class="fw-bold">{{ getAccountTypeName(formData.accountType) }}</div>
            <small class="text-muted">{{ formData.currency }} Account</small>
          </div>
          <div class="text-end">
            <div class="fs-5 text-primary">
              {{ formatCurrency(formData.initialBalance || 0, formData.currency) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useBankStore } from '@/stores/bank.js';

const bankStore = useBankStore();
const isSubmitting = ref(false);
const error = ref(null);
const success = ref(null);

const formData = reactive({
  accountType: '',
  currency: 'USD',
  initialBalance: 0,
  description: ''
});

function getCurrencySymbol(currency) {
  const symbols = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
    'CHF': 'CHF'
  };
  return symbols[currency] || currency;
}

function getAccountTypeName(type) {
  const names = {
    'checking': 'Checking Account',
    'savings': 'Savings Account',
    'business': 'Business Account',
    'investment': 'Investment Account'
  };
  return names[type] || type;
}

function formatCurrency(amount, currency) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
}

async function handleSubmit() {
  error.value = null;
  success.value = null;
  isSubmitting.value = true;

  try {
    // Stage the account creation as a transaction
    const accountCreationTx = {
      type: 'CREATE_ACCOUNT',
      account_type: formData.accountType,
      currency: formData.currency,
      initial_balance: formData.initialBalance || 0,
      description: formData.description || `New ${getAccountTypeName(formData.accountType)}`,
      timestamp: Date.now()
    };

    await bankStore.addTransactionToStage(accountCreationTx);

    success.value = 'Account creation staged successfully! Review your changes to proceed.';

    // Reset form after a delay
    setTimeout(() => {
      formData.accountType = '';
      formData.currency = 'USD';
      formData.initialBalance = 0;
      formData.description = '';
      success.value = null;
    }, 2000);

  } catch (err) {
    console.error('Failed to stage account creation:', err);
    error.value = err.message || 'Failed to stage account creation. Please try again.';
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css");

.create-account-form {
  max-width: 100%;
}

.form-label {
  font-weight: 500;
}

.input-group-text {
  min-width: 50px;
  justify-content: center;
}
</style>

