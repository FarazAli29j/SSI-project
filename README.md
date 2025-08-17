# 🎙️ Voice Assistant (FastAPI + React + Whisper + TTS)

## 📌 Overview
This project is a **voice-enabled assistant** that lets you:
- Record audio from the microphone (via terminal or frontend).
- Convert recorded audio to `.wav` using **FFmpeg**.
- Send audio to a **FastAPI backend**.
- Transcribe audio into text using **OpenAI Whisper**.
- Generate voice responses using **Text-to-Speech (TTS)**.
- Connect with a **React frontend** for user interaction.

---

## 🚀 Key Features
- 🎤 **Microphone Recording**: Capture audio using FFmpeg.
- 🔊 **Speech-to-Text (STT)**: Transcribes audio with Whisper.
- 🗣️ **Text-to-Speech (TTS)**: Converts responses back to audio.
- ⚡ **FastAPI Backend**: Handles API routes for transcription & TTS.
- 🌐 **React Frontend**: Provides a user-friendly interface.
- 🔄 Supports file upload and live mic input (hybrid workflow).

---

## 📦 Libraries & Tools Used
### Python Dependencies
- `fastapi` → API framework
- `uvicorn` → ASGI server for FastAPI
- `pydantic` → Data validation
- `openai` → Whisper + TTS APIs
- `soundfile` / `pydub` → Audio file handling
- `ffmpeg-python` → Audio processing
- `python-multipart` → File uploads

### System Dependency
- **FFmpeg** → Required for:
  - Recording from microphone
  - Converting audio formats (mp3 ↔ wav)
  - Preprocessing before transcription  

Install on macOS:
```bash
brew install ffmpeg
