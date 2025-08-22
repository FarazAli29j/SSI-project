// Recorder.js
import React, { useState } from "react";
import { startRecording, stopRecording } from "./mic";

export default function Recorder() {
  const [isRecording, setIsRecording] = useState(false);

  const handleRecordToggle = async () => {
    if (!isRecording) {
      // Start
      await startRecording();
      setIsRecording(true);
    } else {
      // Stop
      try {
        const audioBlob = await stopRecording();
        console.log("Got blob:", audioBlob);

        // Example: play it back immediately
        const audioURL = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioURL);
        audio.play();

      } catch (err) {
        console.error("Stop error:", err);
      }
      setIsRecording(false);
    }
  };

  return (
    <button
      onClick={handleRecordToggle}
      className="p-3 rounded bg-blue-600 text-white"
    >
      {isRecording ? "Stop Recording" : "Start Recording"}
    </button>
  );
}
