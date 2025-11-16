<template>
  <div class="container mt-4">
    <div class="row justify-content-center">
      <div class="col-md-10 col-lg-8">

        <h2>Review Your Changes</h2>
        <p class="text-muted">You have {{ store.stagedTransactions.length }} staged change(s). Please review and confirm.</p>

        <div v-if="store.stagedTransactions.length === 0" class="alert alert-warning">
          You have no changes to review.
          <button @click="$router.push('/operations')" class="btn btn-link p-0 ms-1">Stage a new operation.</button>
        </div>

        <!-- Account Balances with Projected View -->
        <AccountBalances v-if="store.stagedTransactions.length > 0" :auto-refresh="true" class="mb-4" />

        <!-- Main Diff Card -->
        <div v-if="store.stagedTransactions.length > 0" class="card shadow-sm">
          <div class="card-header">
            <h5 class="mb-0">Staged Transactions</h5>
          </div>
          <div class="card-body">
            <!-- Transaction List -->
            <div class="mb-4">
              <ul class="list-group">
                <li v-for="tx in store.stagedTransactions" :key="tx.id"
                    class="list-group-item">
                  <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                      <div class="d-flex align-items-center gap-2">
                        <i :class="getTransactionIcon(tx)"></i>
                        <strong>{{ formatTransactionType(tx.type) }}</strong>
                      </div>
                      <small class="text-muted d-block mt-1">{{ tx.description || 'No description' }}</small>
                      <small class="text-muted d-block">
                        <i class="bi bi-clock"></i> {{ formatDate(tx.timestamp) }}
                      </small>
                      <!-- Additional details for CREATE_ACCOUNT -->
                      <div v-if="tx.type === 'CREATE_ACCOUNT'" class="mt-2">
                        <span class="badge bg-info me-1">{{ formatAccountTypeName(tx.account_type) }}</span>
                        <span class="badge bg-secondary">{{ tx.currency }}</span>
                      </div>
                    </div>
                    <div class="text-end">
                      <span :class="getTransactionClass(tx)" style="font-size: 1.1rem; font-weight: 600;">
                        {{ formatTransactionAmount(tx) }}
                      </span>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="card-footer d-flex justify-content-between">
            <button class="btn btn-outline-danger" @click="discardChanges">
              <i class="bi bi-trash"></i> Discard All Changes
            </button>
            <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#confirmModal">
              Confirm & Authorize...
              <i class="bi bi-shield-check"></i>
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>

  <!-- Face Verification Modal -->
  <div class="modal fade" id="confirmModal" tabindex="-1" aria-labelledby="confirmModalLabel" aria-hidden="true" ref="modalEl">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-label" id="confirmModalLabel">Authorize Changes</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <p>Please complete Face Verification to authorize these changes.</p>
          <!-- Using the provided component -->
          <FaceVerification @verified="onFaceVerified" />

          <div v-if="authError" class="alert alert-danger mt-3 py-2">
            {{ authError }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useBankStore } from '@/stores/bank.js';
import { useRouter } from 'vue-router';
import { Modal } from 'bootstrap'; // Import Bootstrap's Modal
import FaceVerification from '@/components/FaceVerification.vue';
import AccountBalances from '@/components/AccountBalances.vue';

const store = useBankStore();
const router = useRouter();
const authError = ref(null);
const modalEl = ref(null);
let bsModal = null; // Variable to hold the Bootstrap Modal instance

onMounted(() => {
  if (modalEl.value) {
    bsModal = new Modal(modalEl.value);
  }
});

// --- Helper Functions ---
function formatTransactionType(type) {
  const types = {
    'TRANSFER': 'Transfer',
    'transfer': 'Transfer',
    'debit': 'Withdrawal',
    'credit': 'Deposit',
    'LOAN_ORDER': 'Loan Application',
    'CREATE_ACCOUNT': 'Create Account'
  };
  return types[type] || type;
}

function formatTransactionAmount(tx) {
  if (tx.type === 'CREATE_ACCOUNT') {
    const amount = parseFloat(tx.initial_balance) || 0;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: tx.currency || 'USD'
    }).format(amount);
  }

  const amount = parseFloat(tx.amount) || 0;
  const formatted = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: tx.currency || 'USD'
  }).format(amount);

  if (tx.type === 'debit') return '- ' + formatted;
  if (tx.type === 'credit') return '+ ' + formatted;
  return formatted;
}

function getTransactionClass(tx) {
  if (tx.type === 'debit') return 'text-danger';
  if (tx.type === 'credit') return 'text-success';
  if (tx.type === 'CREATE_ACCOUNT') return 'text-primary';
  return 'text-dark';
}

function formatDate(timestamp) {
  if (!timestamp) return 'N/A';
  return new Date(timestamp).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function getTransactionIcon(tx) {
  const icons = {
    'CREATE_ACCOUNT': 'bi bi-plus-circle text-primary',
    'TRANSFER': 'bi bi-arrow-left-right text-info',
    'transfer': 'bi bi-arrow-left-right text-info',
    'debit': 'bi bi-arrow-down-circle text-danger',
    'credit': 'bi bi-arrow-up-circle text-success',
    'LOAN_ORDER': 'bi bi-cash-coin text-warning'
  };
  return icons[tx.type] || 'bi bi-circle';
}

function formatAccountTypeName(type) {
  const names = {
    'checking': 'Checking',
    'savings': 'Savings',
    'business': 'Business',
    'investment': 'Investment'
  };
  return names[type] || type;
}


onMounted(() => {
  if (modalEl.value) {
    bsModal = new Modal(modalEl.value);
  }
});


// --- Modal & Auth Logic ---

function discardChanges() {
  if (confirm("Are you sure you want to discard all staged changes? This cannot be undone.")) {
    store.discardStagedChanges();
    router.push('/operations');
  }
}

/**
 * This is the magic!
 * It's called by the FaceVerification component's @verified event.
 * That component now needs to emit the *full response data* from the API.
 */
async function onFaceVerified(verificationData) {
  if (verificationData && verificationData.verified && verificationData.mfaToken) {
    try {
      // Call our new Pinia store action
      await store.commitAndAuthorizeStagedChanges(
          verificationData.mfaToken,
          verificationData.mfaTokenExpiry
      );

      // Close modal and navigate
      if (bsModal) {
        bsModal.hide();
      }
      router.push('/changes-upload'); // Go to upload progress view

    } catch (e) {
      authError.value = `Failed to commit: ${e.message}`;
    }
  } else {
    authError.value = "Face verification succeeded, but MFA token was not received.";
  }
}
</script>

<style scoped>
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css");

.text-warning {
  color: #fd7e14 !important;
}
</style>