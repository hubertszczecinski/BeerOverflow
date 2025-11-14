<!-- Registration Form Example -->
<template>
  <form @submit.prevent="submitRegistration">
    <!-- Other form fields -->
    <PhotoCapturer
        @image-captured="handleImageCapture"
        @image-cleared="handleImageCleared"
    />
    <button class="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
            type="submit" :disabled="!capturedImageBlob">Register</button>
  </form>
</template>

<script setup>
import { ref } from 'vue';
import PhotoCapturer from './PhotoCapturer.vue';

const capturedImageBlob = ref(null);

function handleImageCapture({ blob }) {
  capturedImageBlob.value = blob;
}

function handleImageCleared() {
  capturedImageBlob.value = null;
}

async function submitRegistration() {
  const formData = new FormData();
  // Add other fields
  formData.append('image', capturedImageBlob.value, 'capture.jpg');

  // Submit to API
  await fetch('/api/register', { method: 'POST', body: formData });
}
</script>
