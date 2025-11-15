<script setup>
import { ref, onUnmounted, watch } from 'vue';

// --- Emits ---
const emit = defineEmits(['image-captured', 'image-cleared']);

// --- State ---
const isCameraOpen = ref(false);
const stream = ref(null);
const capturedImage = ref(null); // String (data URL) or null

// --- Template Refs ---
const videoElement = ref(null);
const canvasElement = ref(null);

// --- Core Functions ---

/**
 * 1. Starts the camera stream.
 */
async function startCamera() {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop());
  }

  try {
    stream.value = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user' },
      audio: false
    });
    isCameraOpen.value = true;
    capturedImage.value = null; // Clear previous capture
    emit('image-cleared');

  } catch (error) {
    console.error("Error accessing camera:", error);
    alert("Could not access camera. Please grant permission.");
  }
}

// Watch for videoElement to be available and then play
watch(videoElement, (newEl) => {
  if (newEl && stream.value) {
    newEl.srcObject = stream.value;
  }
});

/**
 * 2. Stops the camera stream and releases the device.
 */
function stopCamera() {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop());
  }
  isCameraOpen.value = false;
  stream.value = null;
}

/**
 * 3. Captures a single image from the video feed.
 */
async function captureImage() {
  if (!videoElement.value || capturedImage.value) {
    return;
  }

  const video = videoElement.value;
  const canvas = canvasElement.value;

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const context = canvas.getContext('2d');
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Get the image as a JPEG data URL
  capturedImage.value = canvas.toDataURL('image/jpeg');

  // Convert to blob and emit to parent
  const blob = await dataURLtoBlob(capturedImage.value);
  emit('image-captured', { blob, dataURL: capturedImage.value });
}

/**
 * 4. Allows the user to retake the photo.
 */
function retake() {
  capturedImage.value = null;
  emit('image-cleared');
}

/**
 * 5. Resets the entire component state (hard reset).
 */
function resetCapture() {
  stopCamera();
  capturedImage.value = null;
  emit('image-cleared');
}

// --- Helper Function ---
async function dataURLtoBlob(dataUrl) {
  const res = await fetch(dataUrl);
  return await res.blob();
}

// --- Lifecycle Hook ---
onUnmounted(() => {
  stopCamera();
});

</script>

<template>
  <div class="mb-3">
    <label class="form-label">Identity Photo</label>
    <small class="form-text text-muted d-block mb-2">Please take a clear photo for verification.</small>

    <canvas ref="canvasElement" class="d-none"></canvas>

    <div class="border rounded-lg overflow-hidden" style="border-style: dashed !important;">
      <div v-if="!isCameraOpen" class="d-flex align-items-center justify-content-center" style="height: 288px; background-color: #f8f9fa;">
        <button
            @click="startCamera"
            type="button"
            class="btn btn-primary"
        >
          Start Camera
        </button>
      </div>

      <div v-else class="position-relative">
        <video
            ref="videoElement"
            :srcObject.prop="stream"
            autoplay
            playsinline
            muted
            class="w-100 h-auto"
        ></video>

        <div v-if="capturedImage" class="position-absolute top-0 start-0 w-100 h-100">
          <img :src="capturedImage" alt="Capture preview" class="w-100 h-100" style="object-fit: cover;" />
        </div>
      </div>
    </div>

    <div class="d-flex gap-2 justify-content-center mt-3">

      <button
          v-if="isCameraOpen && !capturedImage"
          @click="captureImage"
          type="button"
          class="btn btn-success flex-grow-1"
      >
        <i class="fas fa-camera"></i> Capture Image
      </button>

      <button
          v-if="isCameraOpen && capturedImage"
          @click="retake"
          type="button"
          class="btn btn-warning flex-grow-1"
      >
        <i class="fas fa-redo"></i> Retake
      </button>

      <button
          v-if="isCameraOpen"
          @click="resetCapture"
          type="button"
          class="btn btn-secondary"
      >
        <i class="fas fa-times"></i> Reset
      </button>
    </div>

  </div>
</template>