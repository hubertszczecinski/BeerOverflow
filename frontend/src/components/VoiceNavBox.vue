<template>
  <div class="voice-recorder">
    <button
        @click="toggleRecording"
        :class="['record-btn', { 'recording': isRecording }]"
    >
      {{ isRecording ? 'Stop Recording' : 'Start Recording' }}
    </button>
    <p v-if="isRecording">Recording... {{ recordingTime }}s</p>
    <p v-if="uploadStatus">{{ uploadStatus }}</p>
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

        const response = await fetch('http://localhost:7000', {
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
/* OKRĄGŁY, BŁĘKITNY, W PRAWYM DOLNYM ROGU – JAK SIRI */
.siri-voice-button {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #1e90ff, #00bfff);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  cursor: pointer;
  box-shadow: 0 8px 25px rgba(30, 144, 255, 0.4);
  z-index: 1000;
  transition: all 0.3s ease;
  animation: float 3s infinite ease-in-out;
  user-select: none;
}

/* Hover – unosi się */
.siri-voice-button:hover {
  transform: translateY(-10px) scale(1.1);
  box-shadow: 0 15px 35px rgba(30, 144, 255, 0.6);
  animation: none;
}

/* Pulsowanie podczas nagrywania – jak Siri */
.siri-voice-button.recording {
  animation: siri-pulse 1.5s infinite;
}

/* Fale dźwięku – jak Siri */
.siri-waves {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.siri-waves span {
  position: absolute;
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  animation: wave 1.6s infinite ease-out;
}

.siri-waves span:nth-child(1) { animation-delay: 0s; }
.siri-waves span:nth-child(2) { animation-delay: 0.4s; }
.siri-waves span:nth-child(3) { animation-delay: 0.8s; }

@keyframes wave {
  0% { transform: scale(0.3); opacity: 1; }
  100% { transform: scale(6); opacity: 0; }
}

@keyframes siri-pulse {
  0% { box-shadow: 0 0 0 0 rgba(30, 144, 255, 0.7); }
  70% { box-shadow: 0 0 0 25px rgba(30, 144, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(30, 144, 255, 0); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* Czas nagrywania – nad przyciskiem */
.recording-time {
  position: absolute;
  top: -28px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.75);
  color: white;
  font-size: 0.8rem;
  padding: 4px 8px;
  border-radius: 12px;
  white-space: nowrap;
  pointer-events: none;
}

/* Mobile */
@media (max-width: 480px) {
  .siri-voice-button {
    width: 60px;
    height: 60px;
    font-size: 1.5rem;
    bottom: 20px;
    right: 20px;
  }
}
</style>