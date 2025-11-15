<template>
  <div class="p-2">
    <h4 class="mb-3">Stage a New Loan Request</h4>
    <form @submit.prevent="stageLoan">

      <div class="mb-3">
        <label for="loanAmount" class="form-label">Loan Amount</label>
        <div class="input-group">
          <span class="input-group-text">$</span>
          <input type="number" class="form-control" id="loanAmount" v-model.number="amount" min="1000" step="100" required />
        </div>
      </div>

      <div class="mb-3">
        <label for="loanTerm" class="form-label">Loan Term (Months)</label>
        <select class="form-select" id="loanTerm" v-model.number="term">
          <option value="12">12 Months</option>
          <option value="24">24 Months</option>
          <option value="36">36 Months</option>
          <option value="60">60 Months</option>
        </select>
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
const amount = ref(5000);
const term = ref(36);
const successMessage = ref('');

function stageLoan() {
  store.addTransactionToStage({
    type: 'LOAN_ORDER',
    amount: amount.value,
    term: term.value,
  });

  successMessage.value = `Loan request for $${amount.value} has been staged.`;
  // Reset form
  amount.value = 5000;
  term.value = 36;

  // Hide message after 3 seconds
  setTimeout(() => { successMessage.value = '' }, 3000);
}
</script>