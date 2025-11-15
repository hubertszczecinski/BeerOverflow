<template>
  <div class="container">
    <div class="login-container">
      <div class="card">
        <div class="card-header text-center">
          <h3>Registration</h3>
        </div>
        <div class="card-body">
          <form @submit.prevent="handleRegister">

            <div class="mb-3">
              <label for="username" class="form-label">Username</label>
              <input type="text" class="form-control" id="username" v-model="form.username" minlength="4" maxlength="20" required>
              <small class="form-text text-muted">4–20 characters</small>
            </div>

            <div class="mb-3">
              <label for="email" class="form-label">Email</label>
              <input type="email" class="form-control" id="email" v-model="form.email" required>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="first_name" class="form-label">First Name</label>
                <input type="text" class="form-control" id="first_name" v-model="form.first_name" required>
              </div>

              <div class="col-md-6 mb-3">
                <label for="last_name" class="form-label">Last Name</label>
                <input type="text" class="form-control" id="last_name" v-model="form.last_name" required>
              </div>
            </div>

            <div class="mb-3">
              <label for="password" class="form-label">Password</label>
              <input type="password" class="form-control" id="password" v-model="form.password" minlength="6" required>
              <small class="form-text text-muted">Minimum 6 characters</small>
            </div>

            <div class="mb-3">
              <label for="password2" class="form-label">Confirm Password</label>
              <input type="password" class="form-control" id="password2" v-model="form.password2" minlength="6" required>
            </div>

            <PhotoCapturer
                @image-captured="handleImageCapture"
                @image-cleared="handleImageCleared"
            />

            <div v-if="errorMessage" class="alert alert-danger" role="alert">
              {{ errorMessage }}
            </div>

            <div class="d-grid">
              <button type="submit" class="btn btn-primary" :disabled="!isFormValid">
                Register
              </button>
            </div>
          </form>

          <hr>

          <div class="text-center">
            <p>Already have an account? <router-link to="/login">Log In</router-link></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import PhotoCapturer from '@/components/PhotoCapturer.vue';

const authStore = useAuthStore();
const capturedImageBlob = ref(null);
const errorMessage = ref(null);

const form = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  password2: '',
});

// --- Form Validation ---
const passwordsMatch = computed(() => {
  return form.password && form.password === form.password2;
});

const isFormValid = computed(() => {
  return passwordsMatch.value &&
      capturedImageBlob.value &&
      form.username &&
      form.email &&
      form.first_name &&
      form.last_name;
});

// --- Event Handlers ---
function handleImageCapture({ blob }) {
  capturedImageBlob.value = blob;
}

function handleImageCleared() {
  capturedImageBlob.value = null;
}

async function handleRegister() {
  errorMessage.value = null; // Clear previous errors

  if (!passwordsMatch.value) {
    errorMessage.value = "Passwords do not match.";
    return;
  }
  if (!capturedImageBlob.value) {
    errorMessage.value = "Please capture a photo.";
    return;
  }
  if (!isFormValid.value) {
    errorMessage.value = "Please fill out all fields.";
    return;
  }

  // Create FormData
  const formData = new FormData();
  formData.append('username', form.username);
  formData.append('email', form.email);
  formData.append('first_name', form.first_name);
  formData.append('last_name', form.last_name);
  formData.append('password', form.password);

  // Append the image blob
  formData.append('photo', capturedImageBlob.value, 'capture.jpg');

  // Submit to the auth store
  await authStore.register(formData);
}
</script>