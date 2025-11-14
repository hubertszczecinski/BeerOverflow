from flask import Flask, request, jsonify
import speech_recognition as sr
import tempfile
import os

app = Flask(__name__)

@app.route('/process-voice', methods=['POST'])
def process_voice():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file'}), 400
    
    audio_file = request.files['audio']
    
    # Save temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
        audio_file.save(tmp.name)
        temp_path = tmp.name
    
    try:
        # Convert MP3 to WAV for speech recognition
        recognizer = sr.Recognizer()
        
        # Use speech_recognition to process audio
        with sr.AudioFile(temp_path) as source:
            audio = recognizer.record(source)
        
        # Recognize speech using Google's speech recognition
        text = recognizer.recognize_google(audio)
        
        # Clean up
        os.unlink(temp_path)
        
        return jsonify({'command': text})
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)