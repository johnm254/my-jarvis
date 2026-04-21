"""
Test ElevenLabs TTS only - hear JARVIS speak without needing Gemini quota.
Run: python test_tts_only.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

tts_key = os.getenv("TTS_API_KEY", "")
if not tts_key or "your_" in tts_key:
    print("❌  TTS_API_KEY not set in .env")
    exit(1)

from elevenlabs import ElevenLabs, VoiceSettings
import sounddevice as sd
import soundfile as sf
import tempfile

client = ElevenLabs(api_key=tts_key)

lines = [
    "Good day, sir. J.A.R.V.I.S. online and fully operational.",
    "All systems are functioning within normal parameters.",
    "Shall I run a diagnostic, sir? Or would you prefer to simply admire the view?",
]

print("🎙️  Playing JARVIS voice samples...\n")

for line in lines:
    print(f"J.A.R.V.I.S.: {line}")
    audio = b"".join(client.text_to_speech.convert(
        voice_id="Adam",   # British male — closest to MCU JARVIS
        text=line,
        model_id="eleven_monolingual_v1",
        voice_settings=VoiceSettings(stability=0.55, similarity_boost=0.8, style=0.1, use_speaker_boost=True),
    ))
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(audio)
        tmp = f.name
    data, sr = sf.read(tmp)
    sd.play(data, sr)
    sd.wait()
    os.unlink(tmp)

print("\n✅  Done.")
