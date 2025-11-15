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
export default {
  name: 'VoiceRecorder',
  data() {
    return {
      isRecording: false,
      mediaRecorder: null,
      audioChunks: [],
      recordingTime: 0,
      recordingTimer: null,
      uploadStatus: ''
    }
  },
  methods: {
    async toggleRecording() {
      if (this.isRecording) {
        this.stopRecording();
      } else {
        await this.startRecording();
      }
    },

    async startRecording() {
      try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        this.audioChunks = [];
        this.mediaRecorder = new MediaRecorder(stream);

        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.audioChunks.push(event.data);
          }
        };

        this.mediaRecorder.onstop = this.handleRecordingStop;

        this.mediaRecorder.start();
        this.isRecording = true;
        this.uploadStatus = '';
        this.startRecordingTimer();

      } catch (error) {
        console.error('Error accessing microphone:', error);
        this.uploadStatus = 'Error accessing microphone';
      }
    },

    stopRecording() {
      if (this.mediaRecorder && this.isRecording) {
        this.mediaRecorder.stop();
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        this.isRecording = false;
        this.stopRecordingTimer();
      }
    },

    handleRecordingStop() {
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
      this.convertAndSendAudio(audioBlob);
    },

    async convertAndSendAudio(blob) {
      try {
        this.uploadStatus = 'Converting audio...';

        // Convert to WAV format
        const wavBlob = await this.convertToWav(blob);

        this.uploadStatus = 'Sending audio...';

        // Send to your localhost endpoint
        const response = await fetch('http://localhost/voice-assist', {
          method: 'POST',
          body: wavBlob,
          headers: {
            'Content-Type': 'audio/wav',
          }
        });

        if (response.ok) {
          const result = await response.text();
          this.uploadStatus = `Success: ${result}`;
        } else {
          this.uploadStatus = 'Upload failed';
        }

      } catch (error) {
        console.error('Error processing audio:', error);
        this.uploadStatus = 'Error processing audio';
      }
    },

    async convertToWav(blob) {
      // Create an AudioContext to process the audio
      const audioContext = new AudioContext();
x``
      // Read the blob as array buffer
      const arrayBuffer = await blob.arrayBuffer();

      // Decode the audio data
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

      // Convert to WAV format
      const wavBuffer = this.audioBufferToWav(audioBuffer);

      return new Blob([wavBuffer], { type: 'audio/wav' });
    },

    audioBufferToWav(audioBuffer) {
      const numChannels = audioBuffer.numberOfChannels;
      const sampleRate = audioBuffer.sampleRate;
      const length = audioBuffer.length * numChannels * 2;
      const buffer = new ArrayBuffer(44 + length);
      const view = new DataView(buffer);

      // WAV header
      const writeString = (offset, string) => {
        for (let i = 0; i < string.length; i++) {
          view.setUint8(offset + i, string.charCodeAt(i));
        }
      };

      writeString(0, 'RIFF');
      view.setUint32(4, 36 + length, true);
      writeString(8, 'WAVE');
      writeString(12, 'fmt ');
      view.setUint32(16, 16, true);
      view.setUint16(20, 1, true);
      view.setUint16(22, numChannels, true);
      view.setUint32(24, sampleRate, true);
      view.setUint32(28, sampleRate * numChannels * 2, true);
      view.setUint16(32, numChannels * 2, true);
      view.setUint16(34, 16, true);
      writeString(36, 'data');
      view.setUint32(40, length, true);

      // Write audio data
      const interleaved = new Float32Array(length / 2);
      for (let channel = 0; channel < numChannels; channel++) {
        const channelData = audioBuffer.getChannelData(channel);
        for (let i = 0; i < channelData.length; i++) {
          interleaved[i * numChannels + channel] = channelData[i];
        }
      }

      let offset = 44;
      for (let i = 0; i < interleaved.length; i++) {
        const sample = Math.max(-1, Math.min(1, interleaved[i]));
        view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
        offset += 2;
      }

      return buffer;
    },

    startRecordingTimer() {
      this.recordingTime = 0;
      this.recordingTimer = setInterval(() => {
        this.recordingTime++;
      }, 1000);
    },

    stopRecordingTimer() {
      if (this.recordingTimer) {
        clearInterval(this.recordingTimer);
        this.recordingTimer = null;
      }
    }
  },

  beforeUnmount() {
    this.stopRecordingTimer();
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
    }
  }
}
</script>

<style scoped>
.record-btn {
  padding: 10px 20px;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  background-color: #4CAF50;
  color: white;
  cursor: pointer;
}

.record-btn.recording {
  background-color: #f44336;
}

.record-btn:hover {
  opacity: 0.8;
}
</style>