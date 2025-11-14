<template>
  <div class="container">
    <section id="accounts" class="my-5">
      <div class="section-header">
        <h2>So that paying is easy</h2>
        <p class="subtitle">Accounts & Cards</p>
      </div>
      <div class="row g-4">
        <div class="col-md-4">
          <ProductCard
            icon="fas fa-wallet"
            title="Open Current Account"
            description="Discover our Current Account, Classic Account, and Premium Account."
            link="#"
            link-text="Learn more"
          />
        </div>
        <div class="col-md-4">
          <ProductCard
            icon="fas fa-building"
            title="Business Account"
            description="The right business account for every company. Now with <strong>2.75%</strong> p.a. on call money."
            link="#"
            link-text="Learn more"
          />
        </div>
        <div class="col-md-4">
          <ProductCard
            icon="fas fa-credit-card"
            title="Credit Cards"
            description="Pay securely and flexibly worldwide. The right credit card for everyone — Visa, Mastercard, or American Express."
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
