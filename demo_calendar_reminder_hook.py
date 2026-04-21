"""Demo script for Calendar Reminder Hook.

This script demonstrates the calendar reminder hook functionality:
1. Initializes the hooks engine
2. Creates and registers the calendar reminder hook
3. Simulates the hook checking calendar every 5 minutes
4. Shows how reminders are delivered for upcoming events

Note: This is a demonstration with mock data since full Google Calendar
integration requires MCP tool setup.
"""

import logging
import time
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class MockSkillRegistry:
    """Mock skill registry for demonstration."""
    
    def get_skill(self, name: str):
        """Return mock manage_calendar skill."""
        if name == "manage_calendar":
            return MockManageCalendarSkill()
        return None


class MockManageCalendarSkill:
    """Mock calendar skill that returns sample events."""
    
    def execute(self, action: str, details: dict):
        """Return mock calendar events."""
        from jarvis.skills.base import SkillResult
        
        # Create mock events - one in 10 minutes, one in 30 minutes
        now = datetime.now()
        
        events = [
            {
                "id": "event_1",
                "title": "Team Standup Meeting",
                "start_time": (now + timedelta(minutes=10)).isoformat(),
                "end_time": (now + timedelta(minutes=25)).isoformat(),
                "description": "Daily standup with the engineering team",
                "location": "Conference Room A"
            },
            {
                "id": "event_2",
                "title": "Lunch with Client",
                "start_time": (now + timedelta(minutes=30)).isoformat(),
                "end_time": (now + timedelta(minutes=90)).isoformat(),
                "description": "Discuss Q1 project requirements",
                "location": "Downtown Restaurant"
            },
            {
                "id": "event_3",
                "title": "Code Review Session",
                "start_time": (now + timedelta(hours=2)).isoformat(),
                "end_time": (now + timedelta(hours=3)).isoformat(),
                "description": "Review PRs for the authentication module",
                "location": "Virtual - Zoom"
            }
        ]
        
        return SkillResult(
            success=True,
            result={"events": events},
            error_message=None,
            execution_time_ms=50
        )


class MockVoiceInterface:
    """Mock voice interface for demonstration."""
    
    def text_to_speech(self, text: str) -> bytes:
        """Mock TTS - just log the text."""
        logger.info(f"[TTS] Converting to speech: {text[:100]}...")
        return b"mock_audio_data"
    
    def play_audio(self, audio: bytes) -> None:
        """Mock audio playback - just log."""
        logger.info(f"[AUDIO] Playing audio ({len(audio)} bytes)")
        logger.info("=" * 80)
        logger.info("🔊 VOICE REMINDER DELIVERED")
        logger.info("=" * 80)


class MockMemorySystem:
    """Mock memory system for demonstration."""
    
    def __init__(self):
        self.preferences = {}
    
    def get_personal_profile(self, user_id: str):
        """Return mock profile."""
        from jarvis.memory.models import PersonalProfile
        return PersonalProfile(
            user_id=user_id,
            first_name="Boss",
            timezone="UTC",
            preferences=self.preferences,
            habits={},
            interests=[],
            communication_style="casual",
            work_hours={"start": "09:00", "end": "18:00"}
        )
    
    def update_preference(self, user_id: str, key: str, value: any) -> None:
        """Store preference."""
        self.preferences[key] = value
        logger.debug(f"Stored preference: {key}")


def main():
    """Run the calendar reminder hook demo."""
    logger.info("=" * 80)
    logger.info("Calendar Reminder Hook Demo")
    logger.info("=" * 80)
    logger.info("")
    
    # Import required components
    from jarvis.hooks.hooks_engine import HooksEngine
    from jarvis.hooks.calendar_reminder_hook import create_calendar_reminder_hook
    
    # Create mock components
    logger.info("Initializing components...")
    hooks_engine = HooksEngine()
    skill_registry = MockSkillRegistry()
    voice_interface = MockVoiceInterface()
    memory_system = MockMemorySystem()
    
    # Create and register the calendar reminder hook
    logger.info("Creating calendar reminder hook...")
    calendar_reminder = create_calendar_reminder_hook(
        hooks_engine=hooks_engine,
        skill_registry=skill_registry,
        voice_interface=voice_interface,
        memory_system=memory_system,
        user_id="demo_user"
    )
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("Hook Configuration:")
    logger.info("  - Check Interval: Every 5 minutes (300 seconds)")
    logger.info("  - Reminder Window: 15 minutes before event")
    logger.info("  - Duplicate Prevention: Enabled")
    logger.info("=" * 80)
    logger.info("")
    
    # Manually trigger the hook to demonstrate functionality
    logger.info("Triggering calendar reminder hook (simulating 5-minute check)...")
    logger.info("")
    
    # First execution - should deliver reminder for event in 10 minutes
    logger.info("--- First Check ---")
    calendar_reminder.execute()
    logger.info("")
    
    time.sleep(2)
    
    # Second execution - should NOT deliver duplicate reminder
    logger.info("--- Second Check (testing duplicate prevention) ---")
    calendar_reminder.execute()
    logger.info("")
    
    # Show delivered reminders
    logger.info("=" * 80)
    logger.info(f"Delivered Reminders: {len(calendar_reminder._delivered_reminders)}")
    for reminder_key in calendar_reminder._delivered_reminders:
        logger.info(f"  - {reminder_key}")
    logger.info("=" * 80)
    logger.info("")
    
    # Show hook status
    logger.info("Hook Status:")
    active_hooks = hooks_engine.list_active_hooks()
    for hook in active_hooks:
        logger.info(f"  - {hook.name} ({hook.hook_type}): {hook.description}")
    logger.info("")
    
    logger.info("=" * 80)
    logger.info("Demo Complete!")
    logger.info("=" * 80)
    logger.info("")
    logger.info("In production, this hook would:")
    logger.info("  1. Run automatically every 5 minutes")
    logger.info("  2. Check Google Calendar via MCP tool")
    logger.info("  3. Deliver voice reminders via ElevenLabs TTS")
    logger.info("  4. Persist delivered reminders across restarts")
    logger.info("")
    
    # Cleanup
    hooks_engine.shutdown()


if __name__ == "__main__":
    main()
