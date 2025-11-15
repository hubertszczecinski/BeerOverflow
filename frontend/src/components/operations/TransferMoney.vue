<template>
  <div class="p-2">
    <h4 class="mb-3">Stage a New Transfer</h4>
    <form @submit.prevent="stageTransfer">
      <div class="mb-3">
        <label for="fromAccount" class="form-label">From Account</label>
        <select class="form-select" id="fromAccount" v-model="from" required>
          <option disabled value="">Select account</option>
          <option v-for="account in store.projectedState.accounts" :key="account.id" :value="account.id">
            {{ account.name }} (Balance: ${{ account.balance.toFixed(2) }})
          </option>
        </select>
      </div>

      <div class="mb-3">
        <label for="toAccount" class="form-label">To Account (IBAN/ID)</label>
        <input type="text" class="form-control" id="toAccount" v-model="to" placeholder="Enter recipient ID" required />
        <!-- In a real app, 'to' would be more complex, maybe a search -->
      </div>

      <div class="mb-3">
        <label for="amount" class="form-label">Amount</label>
        <div class="input-group">
          <span class="input-group-text">$</span>
          <input type="number" class="form-control" id="amount" v-model.number="amount" min="0.01" step="0.01" required />
        </div>
      </div>

      <button type="submit" class="btn btn-success w-100">
        <i class="bi bi-plus-circle"></i> Add to Changes
      </button>

      <div v-if="successMessage" class="alert alert-success mt-3 py-2">
        {{ successMessage }}
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useBankStore } from '@/stores/bank.js';

const store = useBankStore();
const from = ref('');
const to = ref('a2'); // Hardcoding 'Savings' for demo
const amount = ref(100.00);
const successMessage = ref('');

function stageTransfer() {
  store.addTransactionToStage({
    type: 'TRANSFER',
    from: from.value,
    to: to.value,
    amount: amount.value,
  });

  successMessage.value = `Transfer of $${amount.value} to ${to.value} has been staged.`;
  // Reset form
  from.value = '';
  amount.value = 100.00;

  // Hide message after 3 seconds
  setTimeout(() => { successMessage.value = '' }, 3000);
}
</script>