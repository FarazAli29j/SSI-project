import React, { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Mic, UploadCloud } from "lucide-react";

export default function VoiceAssistantUI() {
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [audioFile, setAudioFile] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const handleStartRecording = async () => {
    setTranscript("");
    setRecording(true);
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorderRef.current = new MediaRecorder(stream);

    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunksRef.current.push(event.data);
      }
    };

    mediaRecorderRef.current.onstop = () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
      setAudioFile(audioBlob);
      audioChunksRef.current = [];
      // Send to backend here (later)
    };

    mediaRecorderRef.current.start();
  };

  const handleStopRecording = () => {
    setRecording(false);
    mediaRecorderRef.current.stop();
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    setAudioFile(file);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <Card className="w-full max-w-lg shadow-2xl rounded-2xl">
        <CardContent className="p-6 space-y-4">
          <h1 className="text-2xl font-bold">🎙️ Voice Dictation Assistant</h1>
          <div className="flex flex-col items-center space-y-4">
            <div className="flex gap-4">
              <Button
                onClick={recording ? handleStopRecording : handleStartRecording}
                variant={recording ? "destructive" : "default"}
              >
                <Mic className="mr-2" />
                {recording ? "Stop" : "Record"}
              </Button>
              <Button asChild>
                <label className="cursor-pointer">
                  <UploadCloud className="mr-2" /> Upload Audio
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
              </Button>
            </div>
            <div className="w-full mt-4">
              <p className="text-sm text-gray-600 mb-1">Transcript:</p>
              <div className="p-3 bg-white rounded-md border min-h-[100px]">
                {transcript || "No transcript yet. Speak or upload an audio file."}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
