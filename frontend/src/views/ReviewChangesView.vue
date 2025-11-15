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

        <!-- Main Diff Card -->
        <div v-else class="card shadow-sm">
          <div class="card-header">
            <h5 class="mb-0">Projected State ("The Diff")</h5>
          </div>
          <div class="card-body">
            <!-- Diff View: Accounts -->
            <div class="mb-4">
              <h6>Account Balances</h6>
              <ul class="list-group">
                <li v-for="account in store.projectedState.accounts" :key="account.id"
                    class="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <strong>{{ account.name }}</strong>
                    <br>
                    <small class="text-muted">{{ account.id }}</small>
                  </div>
                  <div>
                    <!-- Show "diff" -->
                    <span v-if="isChanged(account)" class="text-warning me-2" style="font-weight: 600;">
                      ${{ getBaseBalance(account.id).toFixed(2) }}
                      <i class="bi bi-arrow-right-short"></i>
                    </span>
                    <span :class="getChangeClass(account)">
                      ${{ account.balance.toFixed(2) }}
                    </span>
                  </div>
                </li>
              </ul>
            </div>

            <!-- Diff View: New Loans -->
            <div v-if="newLoans.length > 0">
              <h6>New Loan Obligations</h6>
              <ul class="list-group">
                <li v-for="loan in newLoans" :key="loan.id"
                    class="list-group-item list-group-item-success">
                  <strong>New {{ loan.term }}-Month Loan</strong>
                  <span class="float-end"><strong>+${{ loan.amount.toFixed(2) }}</strong></span>
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
import { ref, computed, onMounted } from 'vue';
import { useBankStore } from '@/stores/bank.js';
import { useRouter } from 'vue-router';
import { Modal } from 'bootstrap'; // Import Bootstrap's Modal

// Import the user-provided FaceVerification component
// (Assuming it's in @/components/FaceVerification.vue)
import FaceVerification from '@/components/FaceVerification.vue';

const store = useBankStore();
const router = useRouter();
const authError = ref('');
const modalEl = ref(null); // Ref for the modal DOM element
let bsModal = null; // Variable to hold the Bootstrap Modal instance

onMounted(() => {
  if (modalEl.value) {
    bsModal = new Modal(modalEl.value);
  }
});

// --- Diff Logic ---
function getBaseBalance(accountId) {
  const baseAccount = store.baseState.accounts.find(a => a.id === accountId);
  return baseAccount ? baseAccount.balance : 0;
}

function isChanged(projectedAccount) {
  return projectedAccount.balance !== getBaseBalance(projectedAccount.id);
}

function getChangeClass(projectedAccount) {
  const base = getBaseBalance(projectedAccount.id);
  if (projectedAccount.balance > base) return 'text-success fw-bold';
  if (projectedAccount.balance < base) return 'text-danger fw-bold';
  return 'text-dark';
}

const newLoans = computed(() => {
  return store.projectedState.loans.filter(loan =>
      !store.baseState.loans.some(baseLoan => baseLoan.id === loan.id)
  );
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
  // **CRITICAL**: We need to modify FaceVerification.vue to emit the *data*
  // Let's assume it emits: { verified: true, mfaToken: '...', mfaTokenExpiry: '...' }

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