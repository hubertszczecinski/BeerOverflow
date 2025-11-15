<template>
  <div class="container mt-4">
    <div class="row justify-content-center">
      <div class="col-md-10 col-lg-8">
        <h2 class="mb-3">New Operation</h2>
        <div class="card shadow-sm">
          <div class="card-header">
            <!-- Bootstrap Nav Tabs -->
            <ul class="nav nav-tabs card-header-tabs" id="myTab" role="tablist">
              <li class="nav-item" role="presentation">
                <button class="nav-link active" id="transfer-tab" data-bs-toggle="tab" data-bs-target="#transfer" type="button" role="tab" aria-controls="transfer" aria-selected="true">
                  <i class="bi bi-send"></i> Transfer Money
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button class="nav-link" id="loan-tab" data-bs-toggle="tab" data-bs-target="#loan" type="button" role="tab" aria-controls="loan" aria-selected="false">
                  <i class="bi bi-cash-coin"></i> Order Loan
                </button>
              </li>
            </ul>
          </div>

          <div class="card-body">
            <!-- Tab Content -->
            <div class="tab-content" id="myTabContent">
              <div class="tab-pane fade show active" id="transfer" role="tabpanel" aria-labelledby="transfer-tab">
                <TransferMoney />
              </div>
              <div class="tab-pane fade" id="loan" role="tabpanel" aria-labelledby="loan-tab">
                <OrderLoan />
              </div>
            </div>
          </div>
        </div>

        <!-- Staged Changes Quick-Link -->
        <div v-if="stagedTransactions.length > 0" class="mt-4 text-center">
          <div class="alert alert-info d-flex justify-content-between align-items-center">
             <span>
               You have <strong>{{ stagedTransactions.length }}</strong> change(s) waiting for review.
             </span>
            <button @click="$router.push('/review')" class="btn btn-primary">
              Review Changes
              <i class="bi bi-arrow-right-short"></i>
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useBankStore } from '@/stores/bank.js';
import TransferMoney from '@/components/operations/TransferMoney.vue';
import OrderLoan from '@/components/operations/OrderLoan.vue';

const store = useBankStore();
const stagedTransactions = computed(() => store.stagedTransactions);
</script>

<style scoped>
/* Add Bootstrap Icons */
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css");

.nav-link {
  font-weight: 500;
}
</style>