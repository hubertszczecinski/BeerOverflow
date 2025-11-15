<template>
  <div class="voice-navigation">
    <button
        @click="toggleListening"
        :class="['voice-btn', { 'listening': isListening, 'error': hasError }]"
        :title="isListening ? 'Stop listening' : 'Start voice commands'"
    >
      <i class="fas fa-microphone"></i>
    </button>

    <div v-if="isListening" class="voice-status">
      <div class="pulse-animation"></div>
      <span>Listening... {{ feedback }}</span>
    </div>

    <div v-if="availableCommands.length > 0" class="voice-commands-help">
      <h4>Voice Commands:</h4>
      <div v-for="cmd in availableCommands" :key="cmd.command" class="command-item">
        <strong>"{{ cmd.command }}"</strong> - {{ cmd.description }}
      </div>
    </div>
  </div>
</template>

<script>
import io from 'socket.io-client';

export default {
  name: 'VoiceNavigation',
  data() {
    return {
      isListening: false,
      hasError: false,
      feedback: '',
      mediaRecorder: null,
      audioChunks: [],
      socket: null,
      availableCommands: []
    };
  },
  async mounted() {
    await this.setupVoiceNavigation();
    await this.loadVoiceCommands();
  },
  // Vue 3 lifecycle hook
  beforeUnmount() {
    this.cleanup();
  },
  methods: {
    async setupVoiceNavigation() {
      try {
        // Setup WebSocket connection (Vite: use VITE_WS_URL)
        const wsUrl = (import.meta && import.meta.env && import.meta.env.VITE_WS_URL) || 'http://localhost:5000';
        this.socket = io(wsUrl);

        this.socket.on('connect', () => {
          this.socket.emit('voice_connect');
        });

        this.socket.on('navigate_to', (data) => {
          this.handleNavigation(data);
        });

        this.socket.on('trigger_action', (data) => {
          this.triggerAction(data);
        });

        this.socket.on('voice_feedback', (data) => {
          this.showFeedback(data.text, data.type);
        });

        this.socket.on('voice_error', (data) => {
          this.showError(data.error);
        });

        // Setup audio recording
        await this.setupAudioRecording();

      } catch (error) {
        console.error('Voice navigation setup failed:', error);
        this.showError('Voice setup failed');
      }
    },

    async setupAudioRecording() {
      try {
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

        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.audioChunks.push(event.data);
          }
        };

        this.mediaRecorder.onstop = () => {
          this.processAudioRecording();
        };

      } catch (error) {
        console.error('Audio setup failed:', error);
        this.showError('Microphone access denied');
      }
    },

    async loadVoiceCommands() {
      try {
        const response = await fetch('/api/voice/commands');
        const data = await response.json();
        this.availableCommands = data.commands || [];
      } catch (error) {
        console.error('Failed to load voice commands:', error);
      }
    },

    toggleListening() {
      if (this.isListening) {
        this.stopListening();
      } else {
        this.startListening();
      }
    },

    startListening() {
      if (!this.mediaRecorder) {
        this.showError('Microphone not available');
        return;
      }

      this.isListening = true;
      this.hasError = false;
      this.feedback = 'Speak now...';
      this.audioChunks = [];
      this.mediaRecorder.start(250); // Collect data every 250ms

      // Auto-stop after 5 seconds
      this.autoStopTimer = setTimeout(() => {
        this.stopListening();
      }, 5000);
    },

    stopListening() {
      if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
        this.mediaRecorder.stop();
      }
      this.isListening = false;
      clearTimeout(this.autoStopTimer);
    },

    async processAudioRecording() {
      try {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm;codecs=opus' });

        // Convert to base64 for WebSocket
        const reader = new FileReader();
        reader.onload = () => {
          const base64Audio = reader.result.split(',')[1];
          this.socket.emit('voice_data', { audio: base64Audio });
        };
        reader.readAsDataURL(audioBlob);

      } catch (error) {
        console.error('Audio processing failed:', error);
        this.showError('Failed to process audio');
      }
    },

    handleNavigation(data) {
      this.showFeedback(`Navigating to ${data.recognized_text}`, 'success');

      // Use your existing router
      this.$router.push(data.url);
    },

    triggerAction(data) {
      this.showFeedback(`Executing: ${data.recognized_text}`, 'success');

      // Emit global event for components to handle
      window.dispatchEvent(new CustomEvent('voice-action', {
        detail: data
      }));
    },

    showFeedback(text, type = 'info') {
      this.feedback = text;
      this.hasError = type === 'error';

      // Clear feedback after 3 seconds
      setTimeout(() => {
        this.feedback = '';
        this.hasError = false;
      }, 3000);
    },

    showError(message) {
      this.showFeedback(message, 'error');
      this.isListening = false;
    },

    cleanup() {
      if (this.socket) {
        this.socket.disconnect();
      }
      if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
        this.mediaRecorder.stop();
      }
    }
  }
};
</script>

<style scoped>
.voice-navigation {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.voice-btn {
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.voice-btn.listening {
  background: #2196F3;
  transform: scale(1.1);
}

.voice-btn.error {
  background: #f44336;
}

.voice-status {
  position: absolute;
  bottom: 70px;
  right: 0;
  background: white;
  padding: 10px 15px;
  border-radius: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}

.pulse-animation {
  width: 12px;
  height: 12px;
  background: #2196F3;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.voice-commands-help {
  position: absolute;
  bottom: 70px;
  right: 0;
  width: 300px;
  background: white;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  max-height: 400px;
  overflow-y: auto;
}

.voice-commands-help h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.command-item {
  padding: 5px 0;
  border-bottom: 1px solid #eee;
  font-size: 12px;
}

.command-item:last-child {
  border-bottom: none;
}

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
  100% { transform: scale(0.8); opacity: 1; }
}
</style>