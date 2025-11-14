<!-- TransferPage.vue -->
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isSubmitting = ref(false)

const handleSubmit = async () => {
  isSubmitting.value = true

  // Handle transfer logic here
  try {
    // Your transfer API call
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulated API call

    // On success, you might want to redirect to a success page or back to home
    router.push('/')
  } catch (error) {
    console.error('Transfer error:', error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Make a Transfer
        </h2>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-md">
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label for="amount" class="block text-sm font-medium text-gray-700">Amount</label>
            <input
                type="number"
                id="amount"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label for="recipient" class="block text-sm font-medium text-gray-700">Recipient</label>
            <input
                type="text"
                id="recipient"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label for="account" class="block text-sm font-medium text-gray-700">Account Number</label>
            <input
                type="text"
                id="account"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <button
              type="submit"
              :disabled="isSubmitting"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
          >
            <span v-if="isSubmitting">Processing...</span>
            <span v-else>Complete Transfer</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>