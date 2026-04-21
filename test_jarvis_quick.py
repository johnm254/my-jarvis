"""
JARVIS chat with voice (pyttsx3 offline TTS — no API key needed).
Run: python test_jarvis_quick.py
"""

import os
import sys
import threading
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv
load_dotenv()

# ── Check LLM key ─────────────────────────────────────────────────────────────
api_key = os.getenv("LLM_API_KEY", "")
if not api_key or "your_" in api_key:
    print("❌  LLM_API_KEY is not set in .env")
    sys.exit(1)

print(f"✅  LLM: {os.getenv('LLM_MODEL', 'llama-3.3-70b-versatile')}")
print(f"✅  Voice: pyttsx3 (offline)")
print()

# ── pyttsx3 TTS ───────────────────────────────────────────────────────────────
import pyttsx3

_tts_lock = threading.Lock()

def speak(text: str):
    """Speak in a background thread so typing isn't blocked."""
    def _run():
        with _tts_lock:
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 160)      # slower = more JARVIS-like
                engine.setProperty("volume", 1.0)
                # Pick a male voice if available
                for v in engine.getProperty("voices"):
                    if any(n in v.name.lower() for n in ("david", "mark", "george", "male")):
                        engine.setProperty("voice", v.id)
                        break
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"  [TTS error: {e}]")
    threading.Thread(target=_run, daemon=True).start()

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

# ── Start JARVIS ──────────────────────────────────────────────────────────────
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

    # Register all skills
    from jarvis.skills import (
        SkillRegistry, WebSearchSkill, GetWeatherSkill, SystemStatusSkill,
        RunCodeSkill, GitHubSummarySkill, SetReminderSkill,
        CodeGeneratorSkill, ProjectPlannerSkill, WebsiteBuilderSkill, FileWriterSkill,
        SystemToolsSkill, EmailNotifierSkill,
    )
    registry = SkillRegistry()
    for skill_cls in [
        WebSearchSkill, GetWeatherSkill, SystemStatusSkill,
        RunCodeSkill, GitHubSummarySkill, SetReminderSkill,
        CodeGeneratorSkill, ProjectPlannerSkill, WebsiteBuilderSkill, FileWriterSkill,
        SystemToolsSkill, EmailNotifierSkill,
    ]:
        registry.register_skill(skill_cls())
    brain.skill_registry = registry

    greeting = "JARVIS online. All systems nominal. Good day, sir."
    print(f"⚡  {greeting}\n{'─'*55}")
    speak(greeting)

    session_id = "jarvis_session"

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            farewell = "Shutting down. Good day, sir."
            print(f"\nJARVIS: {farewell}")
            speak(farewell)
            import time; time.sleep(3)
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            farewell = "Very well, sir. Shutting down."
            print(f"\nJARVIS: {farewell}")
            speak(farewell)
            import time; time.sleep(3)
            break

        try:
            context = memory.inject_context(session_id)
            response = brain.process_input(
                user_input=user_input,
                session_id=session_id,
                memory_context=context,
            )
            print(f"\nJARVIS: {response.text}")
            if response.tool_calls:
                print(f"  🔧 {[t['name'] for t in response.tool_calls]}")
            speak(response.text)
        except Exception as e:
            print(f"\n❌  Error: {e}")
