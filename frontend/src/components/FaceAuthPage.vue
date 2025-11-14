<!-- AuthenticatePage.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isAuthenticating = ref(false)
const errorMessage = ref('')

const authenticateWithFace = async () => {
  isAuthenticating.value = true
  errorMessage.value = ''

  try {
    // Call your Flask backend for face verification
    const response = await fetch('/api/face-verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // You might need to send image data or session info
      body: JSON.stringify({
        // Add any required data for face verification
      })
    })

    if (response.ok) {
      const result = await response.json()

      if (result.verified) {
        // If authentication successful, navigate to transfer page
        await router.push('/transfer')
      } else {
        errorMessage.value = 'Face verification failed. Please try again.'
      }
    } else {
      errorMessage.value = 'Authentication service unavailable. Please try again later.'
    }
  } catch (error) {
    console.error('Authentication error:', error)
    errorMessage.value = 'An error occurred during authentication.'
  } finally {
    isAuthenticating.value = false
  }
}

// Optional: Auto-start authentication when component mounts
onMounted(() => {
  // You can automatically start the process or wait for user action
  // authenticateWithFace()
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Identity Verification
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Please authenticate using face verification to proceed with your transfer
        </p>
      </div>

      <div class="mt-8 space-y-6">
        <div class="bg-white p-6 rounded-lg shadow-md">
          <!-- Placeholder for camera/upload interface -->
          <div class="flex justify-center mb-4">
            <div class="w-32 h-32 bg-gray-200 rounded-full flex items-center justify-center">
              <span class="text-gray-500">Camera</span>
            </div>
          </div>

          <p class="text-center text-sm text-gray-600 mb-4">
            Please look directly at your camera for face verification
          </p>

          <button
              @click="authenticateWithFace"
              :disabled="isAuthenticating"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <span v-if="isAuthenticating">Verifying...</span>
            <span v-else>Start Face Verification</span>
          </button>

          <div v-if="errorMessage" class="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {{ errorMessage }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>