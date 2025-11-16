w<template>
  <div v-if="show" class="password-prompt-overlay">
    <div class="password-prompt-modal">
      <div class="password-prompt-header">
        <h5 class="mb-0">
          <i class="bi bi-lock-fill me-2"></i>
          Unlock Your Changes
        </h5>
      </div>

      <div class="password-prompt-body">
        <p class="text-muted mb-3">
          You may have encrypted changes stored locally. Please enter your password to initialize the session and decrypt them for view.
        </p>

        <form @submit.prevent="handleUnlock">
          <div class="mb-3">
            <label for="unlockPassword" class="form-label">Password</label>
            <input
              type="password"
              class="form-control"
              id="unlockPassword"
              v-model="password"
              :disabled="isUnlocking"
              placeholder="Enter your password"
              autocomplete="current-password"
              autofocus
              required
            />
          </div>

          <div v-if="error" class="alert alert-danger py-2 mb-3">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            {{ error }}
          </div>

          <div class="d-flex justify-content-between align-items-center">
            <button
              type="button"
              class="btn btn-outline-secondary"
              @click="handleSkip"
              :disabled="isUnlocking"
            >
              Skip
            </button>

            <button
              type="submit"
              class="btn btn-primary"
              :disabled="!password || isUnlocking"
            >
              <span v-if="isUnlocking" class="spinner-border spinner-border-sm me-2"></span>
              {{ isUnlocking ? 'Unlocking...' : 'Unlock' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useBankStore } from '@/stores/bank.js';

const emit = defineEmits(['unlocked', 'skipped']);

const show = ref(true);
const password = ref('');
const error = ref('');
const isUnlocking = ref(false);

const bankStore = useBankStore();

async function handleUnlock() {
  if (!password.value) return;

  error.value = '';
  isUnlocking.value = true;

  try {
    await bankStore.initializeSession(password.value);
    show.value = false;
    emit('unlocked');
  } catch (err) {
    console.error('Failed to unlock:', err);
    error.value = err.message || 'Invalid password or corrupted data. Please try again.';
  } finally {
    isUnlocking.value = false;
  }
}

function handleSkip() {
  show.value = false;
  emit('skipped');
}
</script>

<style scoped>
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css");

.password-prompt-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(3px);
}

.password-prompt-modal {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 450px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.password-prompt-header {
  padding: 1.5rem;
  border-bottom: 1px solid #dee2e6;
  background: linear-gradient(135deg, #ffb218 0%, #da7400 100%);
  color: white;
  border-radius: 0.5rem 0.5rem 0 0;
}

.password-prompt-body {
  padding: 1.5rem;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.btn-primary {
  background: linear-gradient(135deg, #ffb218 0%, #da7400 100%);
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #ffb218 0%, #da7400 100%);
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.btn-primary:disabled {
  opacity: 0.6;
}
</style>

