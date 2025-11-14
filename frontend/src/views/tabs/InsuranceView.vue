<template>
  <div class="container">
    <section id="insurance" class="my-5">
      <div class="section-header">
        <h2>Insurance & Protection</h2>
        <p class="subtitle">Security for you and your family</p>
      </div>
      <div class="row g-4">
        <div class="col-md-4">
          <ProductCard
            icon="fas fa-shield-alt"
            title="Life Insurance"
            description="Protect your family with the right life insurance."
            link="#"
            link-text="Learn more"
          />
        </div>
        <div class="col-md-4">
          <ProductCard
            icon="fas fa-car"
            title="Car Insurance"
            description="Affordable car insurance with optimal protection for your vehicle."
            link="#"
            link-text="Learn more"
          />
        </div>
        <div class="col-md-4">
          <ProductCard
            icon="fas fa-home"
            title="Home Contents Insurance"
            description="Protect your home furnishings from damage and theft."
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
