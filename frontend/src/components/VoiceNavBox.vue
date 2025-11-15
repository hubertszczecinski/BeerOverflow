<template>
  <div class="audio-recorder">
    <h2>Audio Recorder</h2>

    <div class="controls">
      <button
          @click="startRecording"
          :disabled="isRecording || isLoading"
          class="btn btn-start"
      >
        Start Recording
      </button>

      <button
          @click="stopRecording"
          :disabled="!isRecording || isLoading"
          class="btn btn-stop"
      >
        Stop Recording
      </button>
    </div>

    <div v-if="isRecording" class="recording-indicator">
      ● Recording...
    </div>

    <div v-if="audioUrl" class="preview">
      <h3>Preview:</h3>
      <audio :src="audioUrl" controls class="audio-preview"></audio>
    </div>

    <div v-if="isLoading" class="loading">
      Sending audio...
    </div>

    <div v-if="message" class="message" :class="{ error: isError }">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { MediaRecorder, register } from 'extendable-media-recorder';
import { connect } from 'extendable-media-recorder-wav-encoder';

export default {
  name: 'AudioRecorder',
  data() {
    return {
      isRecording: false,
      isLoading: false,
      mediaRecorder: null,
      audioChunks: [],
      audioUrl: null,
      message: '',
      isError: false
    };
  },
  async mounted() {
    try {
      // Register the WAV encoder
      await register(await connect());
      console.log('WAV encoder registered successfully');
    } catch (error) {
      console.error('Failed to register WAV encoder:', error);
      this.showMessage('Failed to initialize audio recorder', true);
    }
  },
  methods: {
    async startRecording() {
      try {
        this.audioChunks = [];
        this.audioUrl = null;
        this.message = '';

        // Get user media (audio only)
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            channelCount: 1,
            sampleRate: 44100,
            echoCancellation: true,
            noiseSuppression: true
          }
        });

        // Create media recorder with WAV format
        this.mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'audio/wav'
        });

        // Collect data when available
        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data && event.data.size > 0) {
            this.audioChunks.push(event.data);
          }
        };

        // Handle recording stop
        this.mediaRecorder.onstop = this.handleRecordingStop;

        // Start recording
        this.mediaRecorder.start();
        this.isRecording = true;
        this.showMessage('Recording started...');

      } catch (error) {
        console.error('Error starting recording:', error);
        this.showMessage('Error starting recording: ' + error.message, true);
      }
    },

    stopRecording() {
      if (this.mediaRecorder && this.isRecording) {
        this.mediaRecorder.stop();
        this.isRecording = false;

        // Stop all tracks in the stream
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
      }
    },

    async handleRecordingStop() {
      try {
        this.isLoading = true;

        // Create blob from recorded chunks
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });

        // Create URL for preview
        this.audioUrl = URL.createObjectURL(audioBlob);

        // Send to server
        await this.sendAudioToServer(audioBlob);

      } catch (error) {
        console.error('Error processing recording:', error);
        this.showMessage('Error processing recording: ' + error.message, true);
      } finally {
        this.isLoading = false;
      }
    },

    async sendAudioToServer(audioBlob) {
      try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        formData.append('timestamp', new Date().toISOString());

        const response = await fetch('http://localhost:7000/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Server responded with status: ${response.status}`);
        }

        const result = await response.json();
        this.showMessage('Audio sent successfully! Server response: ' + JSON.stringify(result));

      } catch (error) {
        console.error('Error sending audio to server:', error);
        this.showMessage('Error sending audio: ' + error.message, true);
      }
    },

    showMessage(text, isError = false) {
      this.message = text;
      this.isError = isError;

      // Auto-clear success messages after 5 seconds
      if (!isError) {
        setTimeout(() => {
          if (this.message === text) {
            this.message = '';
          }
        }, 5000);
      }
    }
  },
  beforeUnmount() {
    // Clean up
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
    }
    if (this.audioUrl) {
      URL.revokeObjectURL(this.audioUrl);
    }
  }
};
</script>

<style scoped>
.audio-recorder {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.controls {
  margin: 20px 0;
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-start {
  background-color: #4CAF50;
  color: white;
}

.btn-start:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-stop {
  background-color: #f44336;
  color: white;
}

.btn-stop:hover:not(:disabled) {
  background-color: #da190b;
}

.recording-indicator {
  color: #f44336;
  font-weight: bold;
  margin: 10px 0;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.preview {
  margin: 20px 0;
}

.audio-preview {
  width: 100%;
  margin-top: 10px;
}

.loading {
  color: #2196F3;
  font-style: italic;
  margin: 10px 0;
}

.message {
  padding: 10px;
  border-radius: 5px;
  margin: 10px 0;
}

.message:not(.error) {
  background-color: #dff0d8;
  color: #3c763d;
  border: 1px solid #d6e9c6;
}

.message.error {
  background-color: #f2dede;
  color: #a94442;
  border: 1px solid #ebccd1;
}
</style>