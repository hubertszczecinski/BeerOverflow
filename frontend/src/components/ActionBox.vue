<!-- src/components/ActionBox.vue -->
<script setup>
import { inject } from 'vue'

// Get the router provided by App.vue
const router = inject('router')

const handleTransferClick = () => {
  if (router) {
    router.push('/authenticate')
  } else {
    // Fallback navigation
    window.location.href = '/authenticate'
  }
}
</script>

<template>
  <div class="border-gray-600 p-4 rounded-lg shadow-lg flex flex-col items-center justify-center gap-4">
    <img src="../assets/cmz_logo.png" alt="logo" width="40" height="40">
    <h2 class="text-lg font-semibold">Transfer</h2>
    <button
        @click="handleTransferClick"
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-200"
    >
      Transfer now
    </button>
  </div>
</template>