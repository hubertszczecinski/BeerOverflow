<template>
  <div class="card">
    <div class="card-header d-flex align-items-center gap-2">
      <img :src="logo" alt="Face ID" style="height: 28px; width: 28px" />
      <h5 class="mb-0">Face Verification</h5>
    </div>

    <div class="card-body">
      <p class="text-muted mb-3">
        Use your camera to capture a photo and verify your identity.
      </p>

      <PhotoCapturer
        @image-captured="onCaptured"
        @image-cleared="onCleared"
      />

      <div class="d-flex align-items-center gap-2 justify-content-center mt-2">
        <button
          class="btn btn-primary"
          type="button"
          :disabled="!hasImage || isVerifying"
          @click="verifyFace"
        >
          <span v-if="isVerifying" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          {{ isVerifying ? 'Verifying…' : 'Verify Face' }}
        </button>

        <button
          class="btn btn-outline-secondary"
          type="button"
          :disabled="isVerifying || !hasImage"
          @click="clearResult"
        >
          Clear
        </button>
      </div>

      <div class="mt-3" v-if="status !== 'idle'">
        <div v-if="status === 'success'" class="alert alert-success py-2 mb-2">
          Face verified successfully.
        </div>
        <div v-else-if="status === 'error'" class="alert alert-danger py-2 mb-2">
          {{ errorMessage || 'Verification failed. Please retake the photo and try again.' }}
        </div>
        <div v-if="result" class="small text-muted">
          <div>Distance: {{ result.distance ?? 'n/a' }}</div>
          <div>Threshold: {{ result.threshold ?? 'n/a' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import PhotoCapturer from '@/components/PhotoCapturer.vue'
import logo from '@/assets/face_id_logo.png'

const emit = defineEmits(['verified'])

const capturedBlob = ref(null)
const status = ref('idle') // 'idle' | 'verifying' | 'success' | 'error'
const errorMessage = ref('')
const result = ref(null) // { verified, distance, threshold }

const isVerifying = computed(() => status.value === 'verifying')
const hasImage = computed(() => !!capturedBlob.value)

function onCaptured({ blob }) {
  capturedBlob.value = blob
  status.value = 'idle'
  result.value = null
  errorMessage.value = ''
}

function onCleared() {
  capturedBlob.value = null
  status.value = 'idle'
  result.value = null
  errorMessage.value = ''
}

function clearResult() {
  status.value = 'idle'
  result.value = null
  errorMessage.value = ''
}

async function verifyFace() {
  if (!capturedBlob.value) return
  status.value = 'verifying'
  errorMessage.value = ''
  result.value = null

  try {
    const form = new FormData()
    form.append('image', capturedBlob.value, 'capture.jpg')

    const resp = await fetch('/api/verify-face', {
      method: 'POST',
      body: form,
      credentials: 'include',
    })

    const data = await resp.json().catch(() => ({}))

    if (!resp.ok) {
      status.value = 'error'
      errorMessage.value = data?.message || `Request failed (${resp.status})`
      return
    }

    result.value = {
      verified: !!data.verified,
      distance: data.distance,
      threshold: data.threshold,
    }

    status.value = data.verified ? 'success' : 'error'
    if (data.verified) emit('verified')
  } catch (e) {
    status.value = 'error'
    errorMessage.value = e?.message || 'Network error'
    console.error('Verification error:', e)
  }
}
</script>

<style scoped>
.card img { user-select: none; }
</style>

