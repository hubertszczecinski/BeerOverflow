<template>
  <div class="account-balances">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
          <i class="fas fa-wallet me-2"></i>
          {{ showProjected ? 'Projected Balances' : 'Account Balances' }}
        </h5>
        <button
          v-if="bankStore.stagedTransactions.length > 0"
          @click="toggleView"
          class="btn btn-sm btn-outline-primary"
        >
          <i class="fas fa-eye me-1"></i>
          {{ showProjected ? 'Current' : 'Projected' }}
        </button>
      </div>
      <div class="card-body">
        <!-- Loading State -->
        <div v-if="bankStore.isLoading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="text-muted mt-2">Loading accounts...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger">
          <i class="fas fa-exclamation-triangle me-2"></i>
          {{ error }}
        </div>

        <!-- Empty State -->
        <div v-else-if="displayAccounts.length === 0" class="text-center py-4">
          <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
          <p class="text-muted">No accounts found</p>
          <button
            v-if="showCreateButton"
            @click="$emit('create-account')"
            class="btn btn-primary"
          >
            <i class="fas fa-plus me-2"></i>
            Create Account
          </button>
        </div>

        <!-- Accounts List -->
        <div v-else>
          <!-- Individual Accounts -->
          <div
            v-for="account in displayAccounts"
            :key="account.id"
            class="account-item"
            :class="{
              'account-inactive': !account.is_active,
              'account-pending': account._isPending
            }"
          >
            <div class="d-flex justify-content-between align-items-center">
              <div class="account-info">
                <div class="d-flex align-items-center gap-2">
                  <i :class="getAccountIcon(account.account_type)" class="account-icon"></i>
                  <div>
                    <h6 class="mb-0">
                      {{ formatAccountType(account.account_type) }}
                      <span v-if="account._isPending" class="badge bg-warning text-dark ms-2">
                        <i class="fas fa-clock me-1"></i>Pending
                      </span>
                    </h6>
                    <small class="text-muted">{{ account.account_number }}</small>
                  </div>
                </div>
                <span v-if="!account.is_active && !account._isPending" class="badge bg-warning ms-2">Inactive</span>
              </div>
              <div class="account-balance text-end">
                <div class="balance-amount" :class="{ 'text-primary': account.balance >= 0, 'text-danger': account.balance < 0 }">
                  {{ formatCurrency(account.balance, account.currency) }}
                </div>
                <small class="text-muted">{{ account.currency }}</small>
              </div>
            </div>
          </div>

          <!-- Divider -->
          <hr class="my-3">

          <!-- Total Balance -->
          <div class="total-balance">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h5 class="mb-0">
                  <i class="fas fa-calculator me-2"></i>
                  Total Worth (USD equivalent)
                </h5>
                <small class="text-muted">Rough FX conversion applied</small>
              </div>
              <div class="text-end">
                <h4 class="mb-0 text-primary">
                  {{ formatCurrency(displayTotalBalance, 'USD') }}
                </h4>
                <small v-if="showProjected && hasChanges" class="text-success">
                  <i class="fas fa-arrow-up me-1"></i>
                  Change: {{ formatCurrency(displayTotalBalance - bankStore.totalBalance, 'USD') }}
                </small>
              </div>
            </div>
          </div>

          <!-- Staged Changes Notice -->
          <div v-if="bankStore.stagedTransactions.length > 0" class="alert alert-info mt-3 mb-0">
            <i class="fas fa-info-circle me-2"></i>
            {{ bankStore.stagedTransactions.length }} pending transaction(s) staged for review
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useBankStore } from '@/stores/bank';

const props = defineProps({
  showCreateButton: {
    type: Boolean,
    default: false
  },
  autoRefresh: {
    type: Boolean,
    default: false
  }
});

defineEmits(['create-account']);

const bankStore = useBankStore();
const error = ref(null);
const showProjected = ref(false);

const displayAccounts = computed(() => {
  return showProjected.value ? bankStore.projectedAccounts : bankStore.accounts;
});

const displayTotalBalance = computed(() => {
  return showProjected.value ? bankStore.projectedTotalBalance : bankStore.totalBalance;
});

const hasChanges = computed(() => {
  return bankStore.stagedTransactions.length > 0;
});

function toggleView() {
  showProjected.value = !showProjected.value;
}

function formatAccountType(type) {
  const types = {
    checking: 'Checking Account',
    savings: 'Savings Account',
    business: 'Business Account',
    investment: 'Investment Account'
  };
  return types[type] || type;
}

function getAccountIcon(type) {
  const icons = {
    checking: 'fas fa-money-check-alt text-primary',
    savings: 'fas fa-piggy-bank text-success',
    business: 'fas fa-briefcase text-info',
    investment: 'fas fa-chart-line text-warning'
  };
  return icons[type] || 'fas fa-wallet text-secondary';
}

function formatCurrency(amount, currency = 'USD') {
  const value = parseFloat(amount) || 0;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(value);
}

onMounted(async () => {
  if (props.autoRefresh && !bankStore.isLoading && bankStore.accounts.length === 0) {
    try {
      await bankStore.fetchBaseState();
    } catch (err) {
      error.value = 'Failed to load accounts. Please try again.';
      console.error('Failed to fetch accounts:', err);
    }
  }
});
</script>

<style scoped>
.account-balances {
  margin-bottom: 1.5rem;
}

.account-item {
  padding: 1rem;
  border-radius: 0.5rem;
  background-color: #f8f9fa;
  margin-bottom: 0.75rem;
  transition: all 0.2s ease;
}

.account-item:hover {
  background-color: #e9ecef;
  transform: translateX(4px);
}

.account-item:last-child {
  margin-bottom: 0;
}

.account-inactive {
  opacity: 0.6;
}

.account-pending {
  border-left: 4px solid #ffc107;
  animation: pulse-border 2s ease-in-out infinite;
}

@keyframes pulse-border {
  0%, 100% {
    border-left-color: #ffc107;
  }
  50% {
    border-left-color: #ffdb4d;
  }
}

.account-icon {
  font-size: 1.5rem;
}

.balance-amount {
  font-size: 1.25rem;
  font-weight: 600;
}

.total-balance {
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0.5rem;
  color: white;
}

.total-balance h5,
.total-balance h4,
.total-balance small {
  color: white;
}

.total-balance .text-primary {
  color: #ffd700 !important;
}

.total-balance .text-success {
  color: #90ee90 !important;
}
</style>
