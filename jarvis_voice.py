"""
JARVIS - Full voice conversation + music playback.
Speak to JARVIS, it listens, responds, and can play music.

Requirements:
    pip install SpeechRecognition sounddevice yt-dlp playsound3 pyttsx3

Usage:
    python jarvis_voice.py
"""

import os
import sys
import threading
import queue
import tempfile
import subprocess
import time
import numpy as np
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv
load_dotenv()

# ── Check LLM key ─────────────────────────────────────────────────────────────
api_key = os.getenv("LLM_API_KEY", "")
if not api_key or "your_" in api_key:
    print("❌  LLM_API_KEY not set in .env"); sys.exit(1)

print("⚡  Initialising JARVIS ...")

# ── TTS (pyttsx3) ─────────────────────────────────────────────────────────────
import pyttsx3
_tts_lock = threading.Lock()
_speaking = threading.Event()

def _clean_for_speech(text: str) -> str:
    """
    Strip code blocks, file paths, and technical noise before speaking.
    Replace with brief spoken summaries.
    """
    import re

    # Replace code blocks with a brief mention
    def replace_code_block(m):
        lang = m.group(1).strip() if m.group(1) else "code"
        lines = m.group(2).strip().splitlines()
        line_count = len(lines)
        return f"[{line_count} lines of {lang} code]"

    # ```lang\n...\n```
    text = re.sub(r'```(\w*)\n(.*?)```', replace_code_block, text, flags=re.DOTALL)
    # Inline `code`
    text = re.sub(r'`[^`]+`', '', text)
    # Long file paths  e.g. C:\Users\john\jarvis_output\...
    text = re.sub(r'[A-Za-z]:\\[^\s,]+', lambda m: os.path.basename(m.group(0)), text)
    text = re.sub(r'/[^\s,]{20,}', lambda m: os.path.basename(m.group(0)), text)
    # URLs
    text = re.sub(r'https?://\S+', 'the link', text)
    # Markdown headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Markdown bold/italic
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    # Bullet points — keep text, remove symbol
    text = re.sub(r'^\s*[-*•]\s+', '', text, flags=re.MULTILINE)
    # Multiple blank lines → single
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Trim
    return text.strip()


def speak(text: str, wait: bool = False):
    clean = _clean_for_speech(text)
    def _run():
        _speaking.set()
        with _tts_lock:
            try:
                e = pyttsx3.init()
                e.setProperty("rate", 155)
                e.setProperty("volume", 1.0)
                for v in e.getProperty("voices"):
                    if any(n in v.name.lower() for n in ("david", "mark", "george")):
                        e.setProperty("voice", v.id)
                        break
                e.say(clean)
                e.runAndWait()
                e.stop()
            except Exception as ex:
                print(f"[TTS error: {ex}]")
            finally:
                _speaking.clear()
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    if wait:
        t.join()

# ── STT via sounddevice + speech_recognition ──────────────────────────────────
import sounddevice as sd
import speech_recognition as sr

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8

# ── Find best microphone device ───────────────────────────────────────────────
def _find_mic_device() -> int:
    """
    Auto-detect the best available microphone using a priority scoring system.
    Priority: Bluetooth/headset/pods > USB headset > built-in mic > default
    """
    devices = sd.query_devices()
    best_idx = None
    best_score = -1
    best_name = ""
    best_reason = ""

    for i, d in enumerate(devices):
        if d["max_input_channels"] < 1:
            continue
        name = d["name"].lower()
        score = 0
        reason = "generic input"

        # Highest priority: Bluetooth headset / AirPods / wireless pods
        if any(k in name for k in ("airpod", "pods", "bluetooth", "hands-free", "headset bt", "wireless")):
            score = 100
            reason = "Bluetooth headset/pods"
        # High priority: wired headset or headphone mic
        elif any(k in name for k in ("headset", "headphone", "earphone")):
            score = 80
            reason = "wired headset"
        # Medium priority: USB microphone
        elif "usb" in name:
            score = 60
            reason = "USB microphone"
        # Lower priority: built-in / internal mic
        elif any(k in name for k in ("built-in", "internal", "microphone array", "realtek", "conexant")):
            score = 40
            reason = "built-in microphone"
        # Lowest named device
        elif "mic" in name:
            score = 20
            reason = "named microphone"

        if score > best_score:
            best_score = score
            best_idx = i
            best_name = d["name"]
            best_reason = reason

    # Fall back to system default if nothing scored
    if best_idx is None or best_score < 0:
        best_idx = sd.default.device[0]
        best_name = sd.query_devices(best_idx)["name"]
        best_reason = "system default"

    print(f"🎤  Selected mic: [{best_idx}] {best_name}  ({best_reason})")
    return best_idx

MIC_DEVICE = _find_mic_device()

def listen_once(timeout: int = 8) -> str:
    """Record from mic and return transcribed text."""
    sample_rate = 16000
    print("\n🎤  Listening... (speak now)")
    try:
        # Record audio using sounddevice with selected device
        audio_data = sd.rec(
            int(timeout * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
            device=MIC_DEVICE,
        )
        # VAD: stop after ~0.9s of silence post-speech
        chunk = int(0.3 * sample_rate)
        silence_chunks = 0
        started = False
        for i in range(0, int(timeout * sample_rate), chunk):
            sd.sleep(300)
            chunk_data = audio_data[i:i+chunk]
            if len(chunk_data) == 0:
                break
            energy = np.abs(chunk_data).mean()
            if energy > 300:  # raised threshold — ignore background noise
                started = True
                silence_chunks = 0
            elif started:
                silence_chunks += 1
                if silence_chunks >= 3:
                    sd.stop()
                    break
        else:
            sd.stop()

        # Convert to WAV for speech_recognition
        import io, wave
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
        buf.seek(0)

        audio = sr.AudioFile(buf)
        with audio as source:
            audio_data_sr = recognizer.record(source)

        text = recognizer.recognize_google(audio_data_sr)
        print(f"You: {text}")
        return text

    except sr.UnknownValueError:
        print("  [Could not understand — speak clearly and try again]")
        return ""
    except sr.RequestError as e:
        print(f"  [STT error: {e}]")
        return ""
    except Exception as e:
        print(f"  [Listen error: {e}]")
        return ""

# ── Music player ──────────────────────────────────────────────────────────────
_music_process = None
_music_thread = None

def play_music(query: str):
    """Open YouTube search in browser — instant, no dependencies."""
    def _play():
        try:
            import webbrowser
            speak(f"Opening YouTube for {query}, sir.", wait=True)
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            print(f"  🎵 Opened YouTube: {query}")
        except Exception as e:
            print(f"  [Music error: {e}]")
            speak("I couldn't open YouTube, sir.", wait=True)

    threading.Thread(target=_play, daemon=True).start()

def stop_music():
    global _music_process
    if _music_process and _music_process.poll() is None:
        _music_process.terminate()
        _music_process = None
        speak("Music stopped, sir.")
    else:
        speak("Nothing is currently playing, sir.")

# ── Mock Supabase ─────────────────────────────────────────────────────────────
mock_db = MagicMock()
mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
    "user_id": "default_user", "first_name": "sir", "timezone": "UTC",
    "preferences": {}, "habits": {}, "interests": [],
    "communication_style": "formal",
    "work_hours": {"start": "09:00", "end": "18:00"},
}]
mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
mock_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": "1"}]
mock_db.rpc.return_value.execute.return_value.data = []

# ── Main loop ─────────────────────────────────────────────────────────────────
with patch("jarvis.memory.memory_system.create_client", return_value=mock_db):
    from jarvis.config import Configuration
    from jarvis.brain.brain import Brain
    from jarvis.memory.memory_system import MemorySystem

    config = Configuration(
        llm_api_key=api_key,
        llm_model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
        supabase_url="https://mock.supabase.co",
        supabase_key="mock_key",
        jwt_secret="mock_secret",
    )

    memory = MemorySystem(config)
    brain = Brain(config)

    # Register all skills including new ones
    from jarvis.skills import (
        SkillRegistry, WebSearchSkill, GetWeatherSkill, SystemStatusSkill,
        RunCodeSkill, GitHubSummarySkill, SetReminderSkill,
        CodeGeneratorSkill, ProjectPlannerSkill, WebsiteBuilderSkill, FileWriterSkill,
        SystemToolsSkill, EmailNotifierSkill, MusicPlayerSkill, DevToolsSkill,
    )
    registry = SkillRegistry()
    for skill_cls in [
        WebSearchSkill, GetWeatherSkill, SystemStatusSkill,
        RunCodeSkill, GitHubSummarySkill, SetReminderSkill,
        CodeGeneratorSkill, ProjectPlannerSkill, WebsiteBuilderSkill, FileWriterSkill,
        SystemToolsSkill, EmailNotifierSkill, MusicPlayerSkill, DevToolsSkill,
    ]:
        registry.register_skill(skill_cls())
    brain.skill_registry = registry

    print("\n" + "─"*55)
    greeting = "JARVIS online. All systems nominal. Good day, sir."
    print(f"⚡  {greeting}")
    print("─"*55)
    print("   Speak to JARVIS. Say 'stop music' to stop playback.")
    print("   Say 'goodbye' or press Ctrl+C to exit.\n")
    speak(greeting, wait=True)

    session_id = "jarvis_voice_session"

    while True:
        try:
            # Wait for JARVIS to finish speaking before listening
            while _speaking.is_set():
                time.sleep(0.1)

            user_input = listen_once(timeout=8)

            if not user_input:
                continue

            lower = user_input.lower()

            # ── Direct music commands (bypass brain/tool call issues) ─────────
            def _extract_query(text, prefixes):
                t = text.lower()
                for p in sorted(prefixes, key=len, reverse=True):
                    if t.startswith(p):
                        return text[len(p):].strip()
                return text.strip()

            if any(lower.startswith(p) for p in ("play ", "play some", "put on", "play me")):
                query = _extract_query(user_input, ["play some", "play me some", "play me", "put on", "play"])
                if query:
                    from jarvis.skills.music_player import MusicPlayerSkill, _play_on_youtube
                    threading.Thread(target=_play_on_youtube, args=(query,), daemon=True).start()
                    msg = f"Playing {query} on YouTube, sir."
                    print(f"\nJARVIS: {msg}")
                    speak(msg)
                    continue

            if any(w in lower for w in ("stop music", "stop the music", "pause music", "stop playing")):
                from jarvis.skills.music_player import MusicPlayerSkill
                ms = MusicPlayerSkill()
                ms.execute(action="stop")
                msg = "Music stopped, sir."
                print(f"\nJARVIS: {msg}"); speak(msg)
                continue

            if any(w in lower for w in ("volume up", "increase volume", "louder", "turn it up", "turn up the volume")):
                from jarvis.skills.music_player import _change_volume
                vol = _change_volume(+0.10)
                msg = f"Volume up to {vol} percent, sir."
                print(f"\nJARVIS: {msg}"); speak(msg); continue

            if any(w in lower for w in ("volume down", "decrease volume", "quieter", "turn it down", "lower the volume", "turn down")):
                from jarvis.skills.music_player import _change_volume
                vol = _change_volume(-0.10)
                msg = f"Volume down to {vol} percent, sir."
                print(f"\nJARVIS: {msg}"); speak(msg); continue

            if "mute" in lower and "unmute" not in lower:
                from jarvis.skills.music_player import _mute_toggle
                _mute_toggle(True)
                msg = "Audio muted, sir."; print(f"\nJARVIS: {msg}"); speak(msg); continue

            if "unmute" in lower:
                from jarvis.skills.music_player import _mute_toggle
                _mute_toggle(False)
                msg = "Audio unmuted, sir."; print(f"\nJARVIS: {msg}"); speak(msg); continue

            # ── Exit ──────────────────────────────────────────────────────────
            if any(w in lower for w in ("goodbye", "shut down", "exit", "quit")):
                farewell = "Very well, sir. Shutting down. Good day."
                print(f"\nJARVIS: {farewell}")
                speak(farewell, wait=True)
                break

            # ── Brain response ────────────────────────────────────────────────
            context = memory.inject_context(session_id)
            tool_defs = registry.get_tool_definitions()
            response = brain.process_input(
                user_input=user_input,
                session_id=session_id,
                memory_context=context,
                tool_definitions=tool_defs,
            )

            # ── Execute any tool calls the brain requested ────────────────────
            if response.tool_calls:
                for tc in response.tool_calls:
                    tool_name = tc.get("name", "")
                    params = tc.get("input") or {}  # guard against None
                    if not isinstance(params, dict):
                        params = {}
                    print(f"  🔧 Executing: {tool_name}({list(params.keys())})")
                    result = brain.execute_tool_call(tool_name, params)
                    if result.success:
                        print(f"  ✅ {tool_name}: {str(result.result)[:120]}")
                    else:
                        print(f"  ❌ {tool_name} failed: {result.error_message}")

            print(f"\nJARVIS: {response.text}\n")
            speak(response.text)

        except KeyboardInterrupt:
            farewell = "Shutting down. Good day, sir."
            print(f"\nJARVIS: {farewell}")
            speak(farewell, wait=True)
            break
        except Exception as e:
            print(f"\n❌  Error: {e}")
