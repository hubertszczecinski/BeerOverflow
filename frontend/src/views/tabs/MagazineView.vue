<template>
  <div class="container">
    <section id="magazine" class="my-5">
      <div class="section-header">
        <h2>Always up to date</h2>
        <p class="subtitle">News & Tips</p>
      </div>
      <div class="row g-4">
        <div class="col-md-3">
          <ProductCard
            icon="fas fa-newspaper"
            title="Gold Price Record"
            description="Is it still worth getting in? Current analyses on the gold price."
            link="#"
            link-text="Learn more"
            use-h4
          />
        </div>
        <div class="col-md-3">
          <ProductCard
            icon="fas fa-shopping-cart"
            title="Buy Now, Pay Later"
            description="2 facts that make us think — and alternatives."
            link="#"
            link-text="Learn more"
            use-h4
          />
        </div>
        <div class="col-md-3">
          <ProductCard
            icon="fas fa-plane"
            title="Paying Abroad"
            description="4 tips that could save your vacation."
            link="#"
            link-text="Learn more"
            use-h4
          />
        </div>
        <div class="col-md-3">
          <ProductCard
            icon="fas fa-globe"
            title="U.S. Tariffs"
            description="Where U.S. tariffs could hit Germany — scenarios and tips."
            link="#"
            link-text="Learn more"
            use-h4
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import ProductCard from '@/components/ProductCard.vue';
</script>
