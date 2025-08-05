// src/App.js
import React, { useState } from 'react';
import { FiMic, FiUpload } from 'react-icons/fi';
import './App.css';

function App() {
  const [transcript, setTranscript] = useState('');
  const [recording, setRecording] = useState(false);

  const handleAudioUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      console.log("File selected:", file.name);
      // TODO: Send file to backend
    }
  };

  const handleRecordToggle = () => {
    setRecording(!recording);
    // TODO: Start/stop microphone capture
  };

  return (
    <div className="app-container">
      <h1>🎙️ DevBuddy Voice Assistant</h1>

      <div className="controls">
        <button className="record-btn" onClick={handleRecordToggle}>
          <FiMic size={24} />
          {recording ? 'Stop Recording' : 'Start Recording'}
        </button>

        <label className="upload-label">
          <FiUpload size={24} />
          Upload Audio File
          <input type="file" accept="audio/*" onChange={handleAudioUpload} hidden />
        </label>
      </div>

      <div className="transcript-box">
        <h3>Transcript</h3>
        <p>{transcript || 'No transcription yet.'}</p>
      </div>
    </div>
  );
}

export default App;
