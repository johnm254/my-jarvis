"""Find a working ElevenLabs voice ID by trying known ones."""
from dotenv import load_dotenv; load_dotenv()
import os
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key=os.getenv("TTS_API_KEY"))

# Well-known ElevenLabs pre-made voice IDs (always available)
candidates = [
    ("JBFqnCBsd6RMkjVDRZzb", "George - British male"),
    ("N2lVS1w4EtoT3dr4eOWO", "Callum - British male"),
    ("onwK4e9ZLuTAKqWW03F9", "Daniel - British male"),
    ("pNInz6obpgDQGcFmaJgB", "Adam - classic"),
    ("ErXwobaYiN019PkySvjV", "Antoni"),
    ("EXAVITQu4vr4xnSDxMaL", "Bella"),
    ("21m00Tcm4TlvDq8ikWAM", "Rachel"),
]

print("Testing voices...\n")
for voice_id, name in candidates:
    try:
        audio = b"".join(client.text_to_speech.convert(
            voice_id=voice_id,
            text="Test.",
            model_id="eleven_monolingual_v1",
        ))
        print(f"✅  {name}  |  ID: {voice_id}  |  {len(audio)} bytes")
    except Exception as e:
        print(f"❌  {name}  |  {str(e)[:80]}")
