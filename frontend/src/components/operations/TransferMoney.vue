<template>
  <div class="p-2">
    <h4 class="mb-3">Stage a New Transfer</h4>
    <form @submit.prevent="stageTransfer">
      <!-- FROM ACCOUNT -->
      <div class="mb-3">
        <label for="fromAccount" class="form-label">From Account</label>
        <select class="form-select" id="fromAccount" v-model="from" required>
          <option disabled value="">Select account</option>
          <option v-for="account in store.projectedAccounts" :key="account.id" :value="account.id">
            {{ formatAccountLabel(account) }}
          </option>
        </select>
      </div>

      <!-- TRANSFER MODE -->
      <div class="mb-3">
        <label class="form-label">Transfer Destination</label>
        <div class="btn-group w-100" role="group">
          <button type="button" class="btn" :class="transferMode === 'internal' ? 'btn-primary' : 'btn-outline-primary'" @click="transferMode='internal'">
            <i class="bi bi-house-fill me-1"></i> Internal
          </button>
          <button type="button" class="btn" :class="transferMode === 'external' ? 'btn-primary' : 'btn-outline-primary'" @click="transferMode='external'">
            <i class="bi bi-globe me-1"></i> External
          </button>
        </div>
        <small class="text-muted d-block mt-1" v-if="transferMode==='internal'">Move funds between your own accounts.</small>
        <small class="text-muted d-block mt-1" v-else>Send funds to an external account code / IBAN.</small>
      </div>

      <!-- INTERNAL DESTINATION -->
      <div class="mb-3" v-if="transferMode==='internal'">
        <label for="toInternal" class="form-label">Destination Account</label>
        <select class="form-select" id="toInternal" v-model="toInternal" required>
            <option disabled value="">Select destination account</option>
            <option v-for="account in internalDestinationAccounts" :key="account.id" :value="account.id">
              {{ formatAccountLabel(account) }}
            </option>
        </select>
        <small class="text-muted">You cannot select the same account as the source.</small>
      </div>

      <!-- EXTERNAL DESTINATION -->
      <div class="mb-3" v-if="transferMode==='external'">
        <label for="toExternal" class="form-label">Recipient Account Code / IBAN</label>
        <input type="text" class="form-control" id="toExternal" v-model.trim="toExternal" :class="{'is-invalid': externalError}" placeholder="e.g. DE89 3704 0044 0532 0130 00" required />
        <div class="invalid-feedback" v-if="externalError">{{ externalError }}</div>
        <small class="text-muted">Enter a valid external account identifier.</small>
      </div>

      <!-- AMOUNT -->
      <div class="mb-3">
        <label for="amount" class="form-label">Amount</label>
        <div class="input-group">
          <span class="input-group-text">$</span>
          <input type="number" class="form-control" id="amount" v-model.number="amount" min="0.01" step="0.01" required />
        </div>
      </div>

      <!-- OPTIONAL DESCRIPTION -->
      <div class="mb-3">
        <label for="description" class="form-label">Description (Optional)</label>
        <input type="text" id="description" class="form-control" v-model.trim="description" placeholder="e.g. Rent payment, Savings move" />
      </div>

      <button type="submit" class="btn btn-success w-100" :disabled="submitDisabled">
        <i class="bi bi-plus-circle"></i> Add to Changes
      </button>

      <div v-if="successMessage" class="alert alert-success mt-3 py-2">
        {{ successMessage }}
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useBankStore } from '@/stores/bank.js';

const store = useBankStore();
const from = ref('');
const transferMode = ref('internal'); // 'internal' | 'external'
const toInternal = ref('');
const toExternal = ref('');
const amount = ref(100.00);
const description = ref('');
const successMessage = ref('');
const externalError = ref(null);

function formatAccountLabel(acc) {
  const typeNames = { checking: 'Checking', savings: 'Savings', business: 'Business', investment: 'Investment' };
  const type = typeNames[acc.account_type] || acc.account_type || acc.name || 'Account';
  const last4 = acc.account_number ? acc.account_number.slice(-4) : (acc.id || '').toString().slice(-4);
  const currency = acc.currency || 'USD';
  const bal = typeof acc.balance === 'number' ? acc.balance : parseFloat(acc.balance || 0);
  const balFmt = new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(bal);
  return `${type} • ${last4} — ${balFmt}`;
}

const internalDestinationAccounts = computed(() => {
  return store.projectedAccounts.filter(a => a.id !== from.value);
});

const submitDisabled = computed(() => {
  if (!from.value) return true;
  if (amount.value <= 0) return true;
  if (transferMode.value === 'internal') return !toInternal.value;
  if (transferMode.value === 'external') return !toExternal.value || !!externalError.value;
  return false;
});

function validateExternal() {
  if (transferMode.value !== 'external') {
    externalError.value = null;
    return;
  }
  if (!toExternal.value) {
    externalError.value = 'Account code is required';
    return;
  }
  // Very loose pattern: alphanumeric + spaces up to 34 chars
  const cleaned = toExternal.value.replace(/\s+/g, '');
  if (!/^[A-Za-z0-9]{6,34}$/.test(cleaned)) {
    externalError.value = 'Invalid format';
  } else {
    externalError.value = null;
  }
}

function stageTransfer() {
  validateExternal();
  if (submitDisabled.value) return;

  const txBase = {
    type: 'TRANSFER',
    from: from.value,
    amount: amount.value,
    description: description.value || undefined,
    mode: transferMode.value
  };

  let tx;
  if (transferMode.value === 'internal') {
    tx = { ...txBase, to: toInternal.value, internal: true };
  } else {
    tx = { ...txBase, to: toExternal.value, internal: false, external_code: toExternal.value };
  }

  store.addTransactionToStage(tx);

  successMessage.value = transferMode.value === 'internal'
    ? `Transfer of $${amount.value.toFixed(2)} to account ${toInternal.value} staged.`
    : `Transfer of $${amount.value.toFixed(2)} to external account ${toExternal.value} staged.`;

  // Reset form (keep mode for convenience)
  amount.value = 100.00;
  description.value = '';
  if (transferMode.value === 'internal') {
    toInternal.value = '';
  } else {
    toExternal.value = '';
  }

  setTimeout(() => { successMessage.value = '' }, 3000);
}

// Re-validate external code on input change
watch(() => toExternal.value, validateExternal);
watch(() => transferMode.value, () => validateExternal());
</script>

<style scoped>
.btn-group .btn { font-weight: 500; }
</style>
