<template>
  <div class="container">
    <section id="securities" class="my-5">
      <div class="section-header">
        <h2>Securities Trading</h2>
        <p class="subtitle">Professional trading with securities</p>
      </div>
      <div class="row g-4">
        <div class="col-md-6">
          <ProductCard
            icon="fas fa-chart-line"
            title="Stocks & ETFs"
            description="Trade stocks, ETFs, and other securities. Favorable conditions and professional advice."
            link="#"
            link-text="Learn more"
          />
        </div>
        <div class="col-md-6">
          <ProductCard
            icon="fas fa-chart-bar"
            title="Funds & Bonds"
            description="Broadly diversified funds and secure bonds for your investment."
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
