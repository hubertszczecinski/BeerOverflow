<template>
  <div class="product-card" :class="{ 'text-center': centered }">
    <div class="card-icon" v-if="icon">
      <i :class="icon"></i>
    </div>
    <h3 v-if="!useH4">{{ title }}</h3>
    <h4 v-else>{{ title }}</h4>
    <p class="card-text" v-if="description" v-html="description"></p>
    <slot name="content"></slot>
    <a v-if="link && linkText" :href="link" class="card-link">
      {{ linkText }} <i class="fas fa-arrow-right ms-1" v-if="!hideArrow"></i>
    </a>
    <slot name="action"></slot>
  </div>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  link: {
    type: String,
    default: '#'
  },
  linkText: {
    type: String,
    default: 'Learn more'
  },
  hideArrow: {
    type: Boolean,
    default: false
  },
  centered: {
    type: Boolean,
    default: false
  },
  useH4: {
    type: Boolean,
    default: false
  }
});
</script>

