<template>
  <div class="container mt-4">
    <div class="row justify-content-center">
      <div class="col-md-10 col-lg-8">
        <h2 class="mb-3">Uploading Changes</h2>

        <!-- Progress Overview Card -->
        <div class="card shadow-sm mb-4">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="mb-0">Upload Progress</h5>
              <span class="badge" :class="statusBadgeClass">{{ statusText }}</span>
            </div>

            <!-- Progress Bar -->
            <div class="progress mb-3" style="height: 30px;">
              <div
                class="progress-bar progress-bar-striped progress-bar-animated"
                :class="progressBarClass"
                role="progressbar"
                :style="{ width: progressPercentage + '%' }"
                :aria-valuenow="progressPercentage"
                aria-valuemin="0"
                aria-valuemax="100"
              >
                {{ progressPercentage }}%
              </div>
            </div>

            <!-- Stats -->
            <div class="row text-center">
              <div class="col-4">
                <div class="text-muted small">Completed</div>
                <div class="h4 mb-0 text-success">{{ completedCount }}</div>
              </div>
              <div class="col-4">
                <div class="text-muted small">Remaining</div>
                <div class="h4 mb-0 text-primary">{{ store.committedTransactions.length }}</div>
              </div>
              <div class="col-4">
                <div class="text-muted small">Total</div>
                <div class="h4 mb-0">{{ totalCount }}</div>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="store.syncError" class="alert alert-danger mt-3 mb-0">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              {{ store.syncError }}
            </div>

            <!-- MFA Required -->
            <div v-if="store.isMfaRequired" class="alert alert-warning mt-3 mb-0">
              <i class="bi bi-shield-lock-fill me-2"></i>
              Face verification expired. Please return to review and re-authorize.
            </div>
          </div>
        </div>

        <!-- Transaction Queue -->
        <div class="card shadow-sm mb-4">
          <div class="card-header">
            <h5 class="mb-0">Transaction Queue</h5>
          </div>
          <div class="card-body">
            <div v-if="store.committedTransactions.length === 0 && completedCount === 0" class="text-center text-muted py-4">
              No transactions in queue.
            </div>
            <ul v-else class="list-group">
              <li
                v-for="(tx, index) in store.committedTransactions"
                :key="tx.id"
                class="list-group-item d-flex justify-content-between align-items-center"
              >
                <div>
                  <strong>{{ formatTransactionType(tx.type) }}</strong>
                  <br>
                  <small class="text-muted">{{ formatTransactionDetails(tx) }}</small>
                </div>
                <div>
                  <span v-if="index === 0" class="spinner-border spinner-border-sm text-primary me-2"></span>
                  <span class="badge bg-secondary">{{ index === 0 ? 'Uploading...' : 'Pending' }}</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="d-flex justify-content-between">
          <button
            class="btn btn-outline-secondary"
            @click="$router.push('/operations')"
            :disabled="isUploading"
          >
            <i class="bi bi-arrow-left"></i> Back to Operations
          </button>

          <button
            v-if="isComplete"
            class="btn btn-success"
            @click="$router.push('/dashboard')"
          >
            <i class="bi bi-check-circle"></i> Go to Dashboard
          </button>

          <button
            v-else-if="store.isMfaRequired"
            class="btn btn-warning"
            @click="$router.push('/review')"
          >
            <i class="bi bi-shield-check"></i> Re-authorize
          </button>

          <button
            v-else-if="store.syncError"
            class="btn btn-primary"
            @click="retryUpload"
          >
            <i class="bi bi-arrow-repeat"></i> Retry
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useBankStore } from '@/stores/bank.js';
import { useRouter } from 'vue-router';

const store = useBankStore();
const router = useRouter();
const completedCount = ref(0);
const totalCount = ref(0);

// Computed Properties
const progressPercentage = computed(() => {
  if (totalCount.value === 0) return 100;
  return Math.round((completedCount.value / totalCount.value) * 100);
});

const isComplete = computed(() => {
  return totalCount.value > 0 && completedCount.value === totalCount.value && !store.syncError;
});

const isUploading = computed(() => {
  return store.committedTransactions.length > 0 && !store.syncError && !store.isMfaRequired;
});

const statusText = computed(() => {
  if (store.isMfaRequired) return 'Authorization Required';
  if (store.syncError) return 'Error';
  if (isComplete.value) return 'Complete';
  if (isUploading.value) return 'Uploading';
  return 'Ready';
});

const statusBadgeClass = computed(() => {
  if (store.isMfaRequired) return 'bg-warning';
  if (store.syncError) return 'bg-danger';
  if (isComplete.value) return 'bg-success';
  if (isUploading.value) return 'bg-primary';
  return 'bg-secondary';
});

const progressBarClass = computed(() => {
  if (store.syncError) return 'bg-danger';
  if (isComplete.value) return 'bg-success';
  return 'bg-primary';
});

// Methods
function formatTransactionType(type) {
  const types = {
    'TRANSFER': 'Money Transfer',
    'LOAN_ORDER': 'Loan Request',
    'CREATE_ACCOUNT': 'Create Account',
    'debit': 'Withdrawal',
    'credit': 'Deposit'
  };
  return types[type] || type;
}

function formatTransactionDetails(tx) {
  if (tx.type === 'TRANSFER') {
    return `$${tx.amount.toFixed(2)} from ${tx.from} to ${tx.to}`;
  } else if (tx.type === 'LOAN_ORDER') {
    return `$${tx.amount.toFixed(2)} for ${tx.term} months`;
  } else if (tx.type === 'CREATE_ACCOUNT') {
    const accountTypes = {
      'checking': 'Checking',
      'savings': 'Savings',
      'business': 'Business',
      'investment': 'Investment'
    };
    const typeName = accountTypes[tx.account_type] || tx.account_type;
    const amount = tx.initial_balance || 0;
    return `${typeName} account with ${new Intl.NumberFormat('en-US', { style: 'currency', currency: tx.currency || 'USD' }).format(amount)}`;
  } else if (tx.type === 'debit' || tx.type === 'credit') {
    return `${new Intl.NumberFormat('en-US', { style: 'currency', currency: tx.currency || 'USD' }).format(tx.amount)}`;
  }
  return JSON.stringify(tx);
}

function retryUpload() {
  store.triggerUploadWorker();
}

// Track progress
let progressInterval = null;

onMounted(() => {
  // Initialize total count
  totalCount.value = store.committedTransactions.length + completedCount.value;

  // Monitor queue changes
  progressInterval = setInterval(() => {
    const currentRemaining = store.committedTransactions.length;
    const newCompleted = totalCount.value - currentRemaining;
    if (newCompleted > completedCount.value) {
      completedCount.value = newCompleted;
    }

    // Auto-redirect when complete
    if (isComplete.value && totalCount.value > 0) {
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);
    }
  }, 500);
});

onUnmounted(() => {
  if (progressInterval) {
    clearInterval(progressInterval);
  }
});
</script>

<style scoped>
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css");

.progress {
  border-radius: 0.5rem;
}

.badge {
  font-size: 0.875rem;
  padding: 0.5rem 1rem;
}
</style>