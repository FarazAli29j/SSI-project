from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import whisper
import sounddevice as sd
import numpy as np
import tempfile
import os
import torchaudio
from scipy.io.wavfile import write as wav_write

#  Initialize FastAPI app
app = FastAPI(title="Whisper Transcription API", description="Speech-to-Text with TTS", version="1.0")

#  Load Whisper model once (so it's reused across requests)
def load_whisper_model(model_size="medium"):
    try:
        return whisper.load_model(model_size)
    except Exception as e:
        print(f"❗ Error loading Whisper model: {e}")
        exit(1)

model = load_whisper_model()


#  Record microphone input (optional feature)
def record_audio_to_file(filename: str):
    print("🎙️ Recording... Press ENTER to stop.")
    samplerate = 16000
    channels = 1
    recording = []

    def callback(indata, frames, time, status):
        if status:
            print(f"⚠️ Recording status: {status}")
        recording.append(indata.copy())

    try:
        with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
            input()
            print("🛑 Stopped recording.")
    except Exception as e:
        print(f"❗ Error during recording: {e}")
        return False

    try:
        audio_data = np.concatenate(recording, axis=0)
        wav_write(filename, samplerate, (audio_data * 32767).astype(np.int16))
        print(f"✅ Audio saved to {filename}")
        return True
    except Exception as e:
        print(f"❗ Error saving audio: {e}")
        return False


# Convert MP3 to WAV (if needed)
def convert_mp3_to_wav(mp3_path):
    wav_path = mp3_path.replace(".mp3", ".wav")
    try:
        waveform, sample_rate = torchaudio.load(mp3_path)
        torchaudio.save(wav_path, waveform, sample_rate)
        return wav_path
    except Exception as e:
        print(f"❗ Error converting MP3 to WAV: {e}")
        return None


#  Transcribe audio using Whisper
def transcribe_audio(file_path):
    print(f"🔍 Transcribing: {file_path}")
    try:
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        print(f"❗ Error during transcription: {e}")
        return None


# Speak transcribed text using system TTS (macOS `say`)
def speak_text(text, voice="Samantha", speed=180):
    """
    Speaks text using macOS 'say' command with custom voice and speed.
    voice: Voice name from `say -v ?`
    speed: Words per minute (default 180)
    """
    if not text:
        print("❗ Nothing to speak.")
        return
    try:
        os.system(f'say -v "{voice}" -r {speed} "{text}"')
        print(f"✅ Spoken with voice '{voice}' at {speed} WPM.")
    except Exception as e:
        print(f"❗ Error during speech synthesis: {e}")


# 🚀 FastAPI Endpoints
@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...), speak: bool = Form(False)):
    """
    Upload an audio file (.wav or .mp3), transcribe it using Whisper,
    and optionally speak the result with system TTS.
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Convert mp3 to wav if needed
        if tmp_path.endswith(".mp3"):
            tmp_path = convert_mp3_to_wav(tmp_path)

        # Run transcription
        transcription = transcribe_audio(tmp_path)

        # Cleanup
        os.remove(tmp_path)

        if not transcription:
            return JSONResponse(content={"error": "Transcription failed"}, status_code=500)

        # Optionally speak the text
        if speak:
            speak_text(transcription)

        return {"transcription": transcription}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Root endpoint
@app.get("/")
def home():
    return {"message": "Welcome to Whisper Transcription API with TTS 🎙️"}


# Run FastAPI only when executing this file directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
