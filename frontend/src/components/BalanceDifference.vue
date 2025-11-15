<template>
  <div v-if="difference !== 0" class="balance-difference" :class="differenceClass">
    <i :class="iconClass"></i>
    <span class="difference-amount">{{ formattedDifference }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  difference: {
    type: Number,
    required: true
  },
  currency: {
    type: String,
    default: 'USD'
  },
  compact: {
    type: Boolean,
    default: false
  }
});

const isPositive = computed(() => props.difference > 0);
const isNegative = computed(() => props.difference < 0);

const differenceClass = computed(() => ({
  'difference-positive': isPositive.value,
  'difference-negative': isNegative.value,
  'difference-compact': props.compact
}));

const iconClass = computed(() => {
  if (isPositive.value) {
    return 'fas fa-arrow-up';
  } else if (isNegative.value) {
    return 'fas fa-arrow-down';
  }
  return '';
});

const formattedDifference = computed(() => {
  const value = Math.abs(props.difference);
  const formatted = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: props.currency
  }).format(value);

  return props.compact ? formatted : formatted;
});
</script>

<style scoped>
.balance-difference {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
}

.balance-difference.difference-compact {
  padding: 0.125rem 0.375rem;
  font-size: 0.75rem;
}

.difference-positive {
  color: #198754;
  background-color: rgba(25, 135, 84, 0.1);
}

.difference-positive i {
  color: #198754;
}

.difference-negative {
  color: #dc3545;
  background-color: rgba(220, 53, 69, 0.1);
}

.difference-negative i {
  color: #dc3545;
}

.difference-amount {
  font-variant-numeric: tabular-nums;
}

/* Animation */
.balance-difference {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>

