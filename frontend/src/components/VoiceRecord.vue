<template>
  <div class="audio-recorder">
    <div class="recorder-controls">
      <button
          @click="startRecording"
          :disabled="isRecording || isLoading"
          class="record-btn"
      >
        {{ isLoading ? 'Loading...' : 'Start Recording' }}
      </button>

      <button
          @click="stopRecording"
          :disabled="!isRecording"
          class="stop-btn"
      >
        Stop Recording
      </button>

      <button
          @click="playRecording"
          :disabled="!audioUrl || isRecording"
          class="play-btn"
      >
        Play
      </button>

      <button
          @click="sendToServer"
          :disabled="!audioUrl || isSending"
          class="send-btn"
      >
        {{ isSending ? 'Sending...' : 'Send to Server' }}
      </button>
    </div>

    <div class="recorder-status">
      <p v-if="isRecording" class="recording-indicator">
        ● Recording... ({{ recordingTime }}s)
      </p>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
      <p v-if="serverResponse" class="server-response">
        Server response: {{ serverResponse }}
      </p>
    </div>

    <div class="server-config">
      <label>
        Server URL:
        <input
            v-model="serverUrl"
            type="text"
            placeholder="http://localhost:3000/upload"
            class="server-input"
        />
      </label>
    </div>

    <div v-if="audioUrl" class="audio-preview">
      <audio :src="audioUrl" controls class="audio-player"></audio>
      <a :href="audioUrl" download="recording.wav" class="download-btn">
        Download Recording
      </a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AudioRecorder',
  data() {
    return {
      isRecording: false,
      isLoading: false,
      isSending: false,
      mediaRecorder: null,
      audioChunks: [],
      audioUrl: null,
      audioBlob: null,
      recordingTime: 0,
      timerInterval: null,
      error: null,
      successMessage: null,
      serverResponse: null,
      serverUrl: 'http://localhost:3000/upload' // Default server URL
    }
  },
  methods: {
    async startRecording() {
      try {
        this.isLoading = true;
        this.error = null;
        this.successMessage = null;
        this.serverResponse = null;

        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            sampleRate: 16000
          }
        });

        this.mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'audio/webm;codecs=opus'
        });

        this.audioChunks = [];

        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.audioChunks.push(event.data);
          }
        };

        this.mediaRecorder.onstop = () => {
          this.createAudioBlob();
          this.stopTimer();
          this.cleanupStream();
        };

        this.mediaRecorder.start(100);
        this.isRecording = true;
        this.startTimer();

      } catch (err) {
        this.error = `Microphone access denied: ${err.message}`;
        console.error('Error starting recording:', err);
      } finally {
        this.isLoading = false;
      }
    },

    stopRecording() {
      if (this.mediaRecorder && this.isRecording) {
        this.mediaRecorder.stop();
        this.isRecording = false;
      }
    },

    createAudioBlob() {
      try {
        this.audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        this.audioUrl = URL.createObjectURL(this.audioBlob);
      } catch (err) {
        this.error = 'Error creating audio file';
        console.error('Error creating audio URL:', err);
      }
    },

    playRecording() {
      if (this.audioUrl) {
        const audioElement = new Audio(this.audioUrl);
        audioElement.play().catch(err => {
          this.error = 'Error playing audio';
          console.error('Error playing audio:', err);
        });
      }
    },

    async sendToServer() {
      if (!this.audioBlob) {
        this.error = 'No recording available to send';
        return;
      }

      this.isSending = true;
      this.error = null;
      this.successMessage = null;
      this.serverResponse = null;

      try {
        // Create FormData to send the file
        const formData = new FormData();
        formData.append('audio', this.audioBlob, 'recording.webm');
        formData.append('timestamp', new Date().toISOString());
        formData.append('duration', this.recordingTime.toString());

        const response = await fetch(this.serverUrl, {
          method: 'POST',
          body: formData,
          // If you need to send JSON instead, use:
          // headers: { 'Content-Type': 'application/json' },
          // body: JSON.stringify({ audio: base64Data, ... })
        });

        if (!response.ok) {
          throw new Error(`Server responded with status: ${response.status}`);
        }

        const result = await response.json();

        this.successMessage = 'Recording sent successfully!';
        this.serverResponse = JSON.stringify(result, null, 2);

        console.log('Server response:', result);

      } catch (err) {
        this.error = `Failed to send recording: ${err.message}`;
        console.error('Error sending to server:', err);
      } finally {
        this.isSending = false;
      }
    },

    // Alternative method to send as base64 encoded string
    async sendAsBase64() {
      if (!this.audioBlob) return;

      try {
        const base64Data = await this.blobToBase64(this.audioBlob);

        const response = await fetch(this.serverUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            audio: base64Data,
            filename: `recording-${Date.now()}.webm`,
            timestamp: new Date().toISOString(),
            duration: this.recordingTime
          })
        });

        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();
        console.log('Base64 upload successful:', result);

      } catch (err) {
        console.error('Error sending base64 data:', err);
      }
    },

    blobToBase64(blob) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          // Remove data URL prefix if present
          const base64 = reader.result.split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    },

    startTimer() {
      this.recordingTime = 0;
      this.timerInterval = setInterval(() => {
        this.recordingTime++;
      }, 1000);
    },

    stopTimer() {
      if (this.timerInterval) {
        clearInterval(this.timerInterval);
        this.timerInterval = null;
      }
    },

    cleanupStream() {
      if (this.mediaRecorder && this.mediaRecorder.stream) {
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
      }
    }
  },
  beforeUnmount() {
    this.stopRecording();
    this.stopTimer();
    this.cleanupStream();

    if (this.audioUrl) {
      URL.revokeObjectURL(this.audioUrl);
    }
  }
}
</script>

<style scoped>
.audio-recorder {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.recorder-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.recorder-controls button {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.recorder-controls button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.record-btn {
  background-color: #4CAF50;
  color: white;
}

.record-btn:hover:not(:disabled) {
  background-color: #45a049;
}

.stop-btn {
  background-color: #f44336;
  color: white;
}

.stop-btn:hover:not(:disabled) {
  background-color: #da190b;
}

.play-btn {
  background-color: #2196F3;
  color: white;
}

.play-btn:hover:not(:disabled) {
  background-color: #0b7dda;
}

.send-btn {
  background-color: #9C27B0;
  color: white;
}

.send-btn:hover:not(:disabled) {
  background-color: #7b1fa2;
}

.download-btn {
  display: inline-block;
  padding: 8px 12px;
  background-color: #ff9800;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  margin-top: 10px;
}

.recording-indicator {
  color: #f44336;
  font-weight: bold;
  animation: pulse 1s infinite;
}

.error-message {
  color: #f44336;
  font-weight: bold;
}

.success-message {
  color: #4CAF50;
  font-weight: bold;
}

.server-response {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
  margin-top: 10px;
  word-break: break-all;
}

.server-config {
  margin: 15px 0;
}

.server-input {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.audio-preview {
  margin-top: 15px;
}

.audio-player {
  width: 100%;
  margin-bottom: 10px;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>