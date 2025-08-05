import whisper
import sounddevice as sd
import numpy as np
import tempfile
import os
import argparse
import torchaudio
from scipy.io.wavfile import write as wav_write

def load_whisper_model(model_size="medium"):
    try:
        return whisper.load_model(model_size)
    except Exception as e:
        print(f"❗ Error loading Whisper model: {e}")
        exit(1)

model = load_whisper_model()

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

def convert_mp3_to_wav(mp3_path):
    wav_path = mp3_path.replace(".mp3", ".wav")
    try:
        waveform, sample_rate = torchaudio.load(mp3_path)
        torchaudio.save(wav_path, waveform, sample_rate)
        return wav_path
    except Exception as e:
        print(f"❗ Error converting MP3 to WAV: {e}")
        return None

def transcribe_audio(file_path):
    print(f"🔍 Transcribing: {file_path}")
    try:
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        print(f"❗ Error during transcription: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Voice to Text Transcription with Whisper")
    parser.add_argument('--mic', action='store_true', help="Record audio from microphone")
    parser.add_argument('--file', type=str, help="Transcribe from an existing audio file (.wav or .mp3)")
    args = parser.parse_args()

    transcription = None

    if args.mic:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            if record_audio_to_file(tmpfile.name):
                transcription = transcribe_audio(tmpfile.name)
            os.remove(tmpfile.name)

    elif args.file:
        input_file = args.file
        if not os.path.isfile(input_file):
            print(f"❗ File not found: {input_file}")
            return
        if input_file.endswith(".mp3"):
            input_file = convert_mp3_to_wav(input_file)
            if not input_file:
                return
        elif not input_file.endswith(".wav"):
            print("❗ Unsupported file format. Use .wav or .mp3.")
            return
        transcription = transcribe_audio(input_file)

    else:
        print("❗ Use --mic to record or --file <path> to transcribe a file.")
        return

    if transcription:
        print("\n📄 Transcribed Text:")
        print("-" * 50)
        print(transcription)
        print("-" * 50)
    else:
        print("❗ No transcription available.")

if __name__ == "__main__":
    main()
