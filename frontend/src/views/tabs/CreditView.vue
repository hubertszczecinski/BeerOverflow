<template>
  <div class="container">
    <section id="credit" class="my-5">
      <div class="section-header">
        <h2>Find the loan that fits you</h2>
        <p class="subtitle">Loans & Financing</p>
      </div>
      <div class="row g-4">
        <div class="col-md-4">
          <ProductCard
            icon="fas fa-hand-holding-usd"
            title="Installment Loan"
            description="Your loan for any purpose. We support you quickly and easily with our installment loan."
            link="#"
            link-text="Learn more"
          />
        </div>
        <div class="col-md-4">
          <ProductCard
            icon="fas fa-credit-card"
            title="Overdraft Facility"
            description="Stay flexible at all times. Get a permanent credit line with the overdraft facility."
            link="#"
            link-text="Learn more"
          />
        </div>
        <div class="col-md-4">
          <ProductCard
            icon="fas fa-home"
            title="Mortgage Financing"
            description="Find the right property financing. Starting at <strong>3.68%</strong> effective annual rate."
            link="#"
            link-text="Learn more"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import ProductCard from '@/components/ProductCard.vue';
</script>
