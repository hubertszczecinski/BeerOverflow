<template>
  <div class="container">
    <section id="savings" class="my-5">
      <div class="section-header">
        <h2>Find the right investment</h2>
        <p class="subtitle">Savings & Investments</p>
      </div>
      <div class="row g-4">
        <div class="col-md-3">
          <ProductCard
            icon="fas fa-piggy-bank"
            title="Call Money Account"
            description="Secure <strong>1.7% interest</strong> p.a. with daily availability."
            link="#"
            link-text="Learn more"
          />
        </div>
        <div class="col-md-3">
          <ProductCard
            icon="fas fa-chart-pie"
            title="Savings Plan Promotion"
            description="5 years with no purchase costs on selected top ETFs & fund savings plans. We're celebrating World Savings Weeks!"
            link="#"
            link-text="View Offer"
          />
        </div>
        <div class="col-md-3">
          <ProductCard
            icon="fas fa-coins"
            title="money mate"
            description="Invest money effortlessly. You decide, our experts invest for you."
            link="#"
            link-text="Learn more"
          />
        </div>
        <div class="col-md-3">
          <ProductCard
            icon="fas fa-briefcase"
            title="Direct Depot"
            description="Your free securities account. Benefit from the opportunities of securities and many advantages."
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
