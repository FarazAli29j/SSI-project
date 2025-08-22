// src/App.js
import React, { useState } from 'react';
import { FiMic, FiUpload, FiVolume2 } from 'react-icons/fi';
import './App.css';
import { startRecording, stopRecording } from "./mic";  // mic.js must exist

function App() {
  const [transcript, setTranscript] = useState('');
  const [recording, setRecording] = useState(false);

  // ✅ Handles manual audio file upload
  const handleAudioUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      console.log("File selected:", file.name);

      const formData = new FormData();
      formData.append("file", file);   // ✅ FIXED: send actual file

      try {
        const response = await fetch("http://localhost:8000/transcribe", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) throw new Error("Upload failed");

        const data = await response.json();
        setTranscript(data.text || "No transcription returned");
      } catch (err) {
        console.error("Upload error:", err);
        setTranscript("❌ Error transcribing file");
      }
    }
  };

  // ✅ Handles live recording start/stop
  const handleRecordToggle = async () => {
    if (!recording) {
      await startRecording();
      setRecording(true);
    } else {
      try {
        const audioBlob = await stopRecording();
        setRecording(false);

        const formData = new FormData();
        formData.append("file", audioBlob, "recording.wav");

        const response = await fetch("http://localhost:8000/transcribe", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) throw new Error("Recording upload failed");

        const data = await response.json();
        setTranscript(data.text || "No transcription returned");
      } catch (err) {
        console.error("Recording error:", err);
        setTranscript("❌ Error transcribing recording");
      }
    }
  };

  // ✅ Send transcript to backend TTS and play
  const handleSpeak = async () => {
    if (!transcript) return;

    try {
      const formData = new FormData();
      formData.append("text", transcript);

      const response = await fetch("http://localhost:8000/speak", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("TTS failed");

      const blob = await response.blob();

      // ✅ Ensure correct type (backend returns AIFF)
      const audioURL = URL.createObjectURL(new Blob([blob], { type: "audio/aiff" }));

      const audio = new Audio(audioURL);
      audio.play().catch((err) => console.error("Playback error:", err));
    } catch (err) {
      console.error("TTS error:", err);
      alert("❌ Error generating speech");
    }
  };

  return (
    <div className="app-container">
      <h1>🎙️ DevBuddy Voice Assistant</h1>

      <div className="controls">
        {/* 🎤 Record Button */}
        <button className="record-btn" onClick={handleRecordToggle}>
          <FiMic size={24} />
          {recording ? 'Stop Recording' : 'Start Recording'}
        </button>

        {/* 📂 Upload Button */}
        <label className="upload-label">
          <FiUpload size={24} />
          Upload Audio File
          <input type="file" accept="audio/*" onChange={handleAudioUpload} hidden />
        </label>

        {/* 🔊 Speak Button */}
        <button className="speak-btn" onClick={handleSpeak} disabled={!transcript}>
          <FiVolume2 size={24} />
          Speak
        </button>
      </div>

      {/* 📝 Transcript Output */}
      <div className="transcript-box">
        <h3>Transcript</h3>
        <p>{transcript || 'No transcription yet.'}</p>
      </div>
    </div>
  );
}

export default App;
