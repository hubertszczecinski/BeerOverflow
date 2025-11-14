function showFaceID(result = null, function_name = null) {
  const overlay = document.getElementById('faceid-overlay');
  const circle = document.getElementById('faceid-circle');
  const tick = document.getElementById('faceid-tick');
  const text = document.getElementById('faceid-text');

  overlay.style.visibility = 'visible';
  circle.classList.add('show');

  if (result === null) {
    return;
  }

  setTimeout(() => {
    if (result) {
      tick.classList.add('show');
      text.textContent = "SUCCESS";
      text.classList.add('show');
    } else {
      circle.classList.add('faceid-fail');
      text.textContent = "FAIL";
      text.classList.add('show');
    }
  }, 1500);

  setTimeout(() => {
    overlay.style.visibility = 'hidden';
    circle.className = 'faceid-circle';
    tick.className = 'faceid-tick';
    text.className = 'faceid-text';
    text.textContent = "";
    window.location.href = function_name;

  }, 4500);
  
  
  // Voice Control Functionality
class VoiceControl {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.init();
    }

    init() {
        // Toggle voice control window
        const toggleBtn = document.getElementById('voice-control-toggle');
        const closeBtn = document.getElementById('voice-control-close');
        const voiceWindow = document.getElementById('voice-control-window');
        const recordBtn = document.getElementById('voice-record-btn');

        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                voiceWindow.classList.toggle('show');
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                voiceWindow.classList.remove('show');
            });
        }

        if (recordBtn) {
            recordBtn.addEventListener('click', () => {
                this.toggleRecording();
            });
        }
    }

    async toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                this.processRecording();
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.updateUI(true);
        } catch (error) {
            console.error('Error starting recording:', error);
            this.updateStatus('Error accessing microphone', 'error');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            this.isRecording = false;
            this.updateUI(false);
        }
    }

    async processRecording() {
        this.updateStatus('Processing voice command...', 'processing');
        
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/mp3' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.mp3');

        try {
            const response = await fetch('http://localhost:8080/process-voice', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                this.handleVoiceCommand(result.command);
            } else {
                throw new Error('Server error');
            }
        } catch (error) {
            console.error('Error processing voice command:', error);
            this.updateStatus('Error processing command', 'error');
            setTimeout(() => this.updateStatus(''), 2000);
        }
    }

    handleVoiceCommand(command) {
        if (!command) {
            this.updateStatus('No command recognized', 'error');
            setTimeout(() => this.updateStatus(''), 2000);
            return;
        }

        const normalizedCommand = command.toLowerCase().trim();
        let targetUrl = null;

        if (normalizedCommand.includes('transfer') || normalizedCommand.includes('send money')) {
            targetUrl = "{{ url_for('main.transfer') }}";
        } else if (normalizedCommand.includes('statement') || normalizedCommand.includes('history')) {
            targetUrl = "{{ url_for('main.statements') }}";
        } else if (normalizedCommand.includes('mortgage') || normalizedCommand.includes('loan')) {
            targetUrl = "{{ url_for('main.mortgage_application') }}";
        } else if (normalizedCommand.includes('dashboard') || normalizedCommand.includes('home')) {
            targetUrl = "{{ url_for('main.dashboard') }}";
        } else if (normalizedCommand.includes('portfolio')) {
            // Handle portfolio navigation
            const portfolioBtn = document.querySelector('.product-card a[href="#"]');
            if (portfolioBtn) portfolioBtn.click();
        }

        if (targetUrl) {
            this.updateStatus('Navigating...', 'success');
            setTimeout(() => {
                window.location.href = targetUrl;
            }, 1000);
        } else {
            this.updateStatus(`Command not recognized: "${command}"`, 'error');
            setTimeout(() => this.updateStatus(''), 3000);
        }
    }

    updateUI(recording) {
        const recordBtn = document.getElementById('voice-record-btn');
        const toggleBtn = document.getElementById('voice-control-toggle');
        const status = document.getElementById('voice-status');

        if (recording) {
            recordBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
            recordBtn.classList.add('btn-danger');
            recordBtn.classList.remove('btn-primary');
            toggleBtn.classList.add('recording');
            this.updateStatus('Recording... Speak now', 'recording');
        } else {
            recordBtn.innerHTML = '<i class="fas fa-microphone"></i> Start Recording';
            recordBtn.classList.remove('btn-danger');
            recordBtn.classList.add('btn-primary');
            toggleBtn.classList.remove('recording');
        }
    }

    updateStatus(message, type = '') {
        const status = document.getElementById('voice-status');
        status.textContent = message;
        status.className = 'voice-status ' + type;
    }
}

// Initialize voice control when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new VoiceControl();
});

}