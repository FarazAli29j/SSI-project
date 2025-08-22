from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import whisper
import tempfile
import os
import torchaudio
from scipy.io.wavfile import write as wav_write
import numpy as np
import sounddevice as sd

# -------------------- Init FastAPI 
app = FastAPI(
    title="Whisper Transcription API",
    description="Speech-to-Text with optional TTS",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Load Whisper
def load_whisper_model(model_size="medium"):
    try:
        return whisper.load_model(model_size)
    except Exception as e:
        print(f"❗ Error loading Whisper model: {e}")
        exit(1)

model = load_whisper_model()


# -------------------- Utility: MP3 → WAV 
def convert_mp3_to_wav(mp3_path):
    wav_path = mp3_path.replace(".mp3", ".wav")
    try:
        waveform, sample_rate = torchaudio.load(mp3_path)
        torchaudio.save(wav_path, waveform, sample_rate)
        return wav_path
    except Exception as e:
        print(f"❗ Error converting MP3 to WAV: {e}")
        return None


# -------------------- Transcription 
def transcribe_audio(file_path):
    print(f"🔍 Transcribing: {file_path}")
    try:
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        print(f"❗ Error during transcription: {e}")
        return None


# -------------------- TTS 
def speak_text(text, voice="Samantha", speed=180, filename="speech.aiff"):
    """
    Generate speech audio file from text (macOS say command).
    Returns path to generated file.
    """
    if not text:
        print("❗ Nothing to speak.")
        return None
    try:
        os.system(f'say -v "{voice}" -r {speed} -o {filename} "{text}"')
        print(f"✅ Audio saved to {filename}")
        return filename
    except Exception as e:
        print(f"❗ Error during speech synthesis: {e}")
        return None


# -------------------- API Endpoints

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...), speak: bool = Form(False)):
    """
    Upload audio (.wav or .mp3), transcribe it with Whisper,
    and optionally return TTS audio of the transcription.
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Convert if mp3
        if tmp_path.endswith(".mp3"):
            tmp_path = convert_mp3_to_wav(tmp_path)

        # Run transcription
        transcription = transcribe_audio(tmp_path)

        # Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        if not transcription:
            return JSONResponse(content={"error": "Transcription failed"}, status_code=500)

        # If speak flag is set, return audio file instead of just text
        if speak:
            audio_path = speak_text(transcription, filename="transcribed_speech.aiff")
            if not audio_path or not os.path.exists(audio_path):
                return JSONResponse(content={"error": "TTS failed"}, status_code=500)
            return FileResponse(audio_path, media_type="audio/aiff", filename="transcribed_speech.aiff")

        return {"text": transcription}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/speak")
async def speak_endpoint(text: str = Form(...)):
    """
    Convert given text to speech and return audio file.
    """
    audio_path = speak_text(text, filename="speech.aiff")
    if not audio_path or not os.path.exists(audio_path):
        return JSONResponse(content={"error": "TTS failed"}, status_code=500)

    return FileResponse(audio_path, media_type="audio/aiff", filename="speech.aiff")


@app.get("/")
def home():
    return {"message": "Welcome to Whisper Transcription API with TTS 🎙️"}


# -------------------- Run FastAPI 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
