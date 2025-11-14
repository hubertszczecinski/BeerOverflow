<script setup>
import { ref, onUnmounted } from 'vue';

// --- State ---
const isCameraOpen = ref(false);
const isUploading = ref(false);
const uploadStatus = ref(''); // e.g., 'Uploading...', 'Success!', 'Error.'
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
    uploadStatus.value = '';
    capturedImage.value = null; // Clear previous capture

  } catch (error) {
    console.error("Error accessing camera:", error);
    uploadStatus.value = "Could not access camera. Please grant permission.";
  }
}

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
function captureImage() {
  if (!videoElement.value || capturedImage.value) {
    // Don't capture if one already exists
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

  // Optionally stop the camera stream after capture
  // stopCamera();
  // ^-- Note: If you stop the camera here, "Retake" would need to call startCamera() again.
  // For a "live retake" experience, we'll leave the stream running.
}

/**
 * 4. Allows the user to retake the photo.
 */
function retake() {
  capturedImage.value = null;
  uploadStatus.value = '';
  // If camera was stopped on capture, you would restart it here.
  // if (!isCameraOpen.value) {
  //   startCamera();
  // }
}

/**
 * 5. Sends the captured image to the backend API.
 */
async function sendImage() {
  if (!capturedImage.value) {
    uploadStatus.value = "Please capture an image first.";
    return;
  }

  isUploading.value = true;
  uploadStatus.value = 'Uploading...';

  try {
    const formData = new FormData();
    const blob = await dataURLtoBlob(capturedImage.value);

    formData.append('image', blob, 'capture.jpg');

    // todo: change this to work for both registration and authentication
    const apiEndpoint = `${import.meta.env.API_BASE_URL}/upload-image`;

    const response = await fetch(apiEndpoint, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    const result = await response.json();
    console.log('Upload successful:', result);
    uploadStatus.value = '✅ Upload successful!';

    // Optionally reset after success
    // resetCapture();

  } catch (error) {
    console.error('Upload failed:', error);
    uploadStatus.value = `Upload failed: ${error.message}`;
  } finally {
    isUploading.value = false;
  }
}

/**
 * 6. Resets the entire component state (hard reset).
 */
function resetCapture() {
  stopCamera();
  capturedImage.value = null;
  uploadStatus.value = '';
  isUploading.value = false;
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
  <div class="max-w-xl mx-auto p-4 bg-white rounded-lg shadow-xl space-y-4">

    <canvas ref="canvasElement" class="hidden"></canvas>

    <div class="border-2 border-dashed border-gray-300 rounded-lg overflow-hidden">
      <div v-if="!isCameraOpen" class="flex items-center justify-center h-72 bg-gray-50">
        <button
            @click="startCamera"
            class="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
        >
          Start Camera
        </button>
      </div>

      <div v-else class="relative">
        <video
            ref="videoElement"
            :srcObject.prop="stream"
            autoplay
            playsinline
            muted
            class="w-full h-auto"
        ></video>

        <div v-if="capturedImage" class="absolute inset-0">
          <img :src="capturedImage" alt="Capture preview" class="w-full h-full object-cover" />
        </div>
      </div>
    </div>

    <div class="flex flex-wrap gap-4 justify-center">

      <button
          v-if="isCameraOpen && !capturedImage"
          @click="captureImage"
          :disabled="isUploading"
          class="flex-1 px-5 py-3 bg-green-500 text-white font-bold rounded-lg shadow hover:bg-green-600 transition disabled:opacity-50"
      >
        Capture Image
      </button>

      <button
          v-if="isCameraOpen && capturedImage"
          @click="retake"
          :disabled="isUploading"
          class="flex-1 px-5 py-2 bg-yellow-500 text-white font-medium rounded-md shadow hover:bg-yellow-600 transition disabled:opacity-50"
      >
        Retake
      </button>

      <button
          v-if="isCameraOpen && capturedImage"
          @click="sendImage"
          :disabled="isUploading"
          class="flex-1 px-5 py-2 bg-purple-600 text-white font-medium rounded-md shadow hover:bg-purple-700 transition disabled:opacity-50"
      >
        <span v-if="isUploading">Uploading...</span>
        <span v-else>Upload Image</span>
      </button>

      <button
          v-if="isCameraOpen"
          @click="resetCapture"
          :disabled="isUploading"
          class="px-5 py-2 bg-gray-500 text-white font-medium rounded-md shadow hover:bg-gray-600 transition disabled:opacity-50"
      >
        Reset
      </button>
    </div>

    <div v-if="uploadStatus" class="text-center font-medium p-2 rounded-md"
         :class="{
           'text-green-700 bg-green-100': uploadStatus.includes('success'),
           'text-red-700 bg-red-100': uploadStatus.includes('failed') || uploadStatus.includes('Could not')
         }"
    >
      {{ uploadStatus }}
    </div>

  </div>
</template>