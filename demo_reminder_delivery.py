"""Demo script for testing reminder delivery hook.

This script demonstrates:
1. Creating reminders using SetReminderSkill
2. Registering the reminder delivery hook
3. Automatic delivery of reminders when they become due
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add jarvis to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jarvis.config import Configuration
from jarvis.memory.memory_system import MemorySystem
from jarvis.voice.voice_interface import VoiceInterface
from jarvis.hooks.hooks_engine import HooksEngine
from jarvis.hooks.reminder_delivery_hook import create_reminder_delivery_hook
from jarvis.skills.set_reminder import SetReminderSkill

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run the reminder delivery demo."""
    # Load environment variables
    load_dotenv()
    
    # Create configuration
    config = Configuration(
        llm_model="claude-sonnet-4-20250514",
        llm_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        voice_enabled=True,
        wake_word="jarvis",
        stt_model="base",
        tts_api_key=os.getenv("ELEVENLABS_API_KEY", ""),
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_key=os.getenv("SUPABASE_KEY", ""),
        dashboard_port=3000,
        jwt_secret=os.getenv("JWT_SECRET", "dev-secret-key"),
        log_level="INFO"
    )
    
    logger.info("Initializing JARVIS components...")
    
    # Initialize Memory System
    memory_system = MemorySystem(config)
    logger.info("Memory System initialized")
    
    # Initialize Voice Interface
    voice_interface = VoiceInterface(
        model_name=config.stt_model,
        elevenlabs_api_key=config.tts_api_key
    )
    logger.info("Voice Interface initialized")
    
    # Initialize Hooks Engine
    hooks_engine = HooksEngine()
    logger.info("Hooks Engine initialized")
    
    # Create and register reminder delivery hook
    logger.info("Registering reminder delivery hook...")
    reminder_delivery_hook = create_reminder_delivery_hook(
        hooks_engine=hooks_engine,
        voice_interface=voice_interface,
        memory_system=memory_system
    )
    logger.info("Reminder delivery hook registered")
    
    # Initialize SetReminderSkill
    set_reminder_skill = SetReminderSkill(memory_system=memory_system)
    logger.info("SetReminderSkill initialized")
    
    # Demo: Create test reminders
    logger.info("\n" + "="*60)
    logger.info("DEMO: Creating test reminders")
    logger.info("="*60)
    
    # Reminder 1: In 30 seconds
    logger.info("\n1. Creating reminder for 30 seconds from now...")
    result1 = set_reminder_skill.execute(
        task="Test reminder - this should trigger in 30 seconds",
        time="in 30 seconds"
    )
    
    if result1.success:
        logger.info(f"✓ Reminder created: {result1.result['reminder_id']}")
        logger.info(f"  Task: {result1.result['task']}")
        logger.info(f"  Scheduled: {result1.result['scheduled_time_human']}")
    else:
        logger.error(f"✗ Failed to create reminder: {result1.error_message}")
    
    # Reminder 2: In 1 minute
    logger.info("\n2. Creating reminder for 1 minute from now...")
    result2 = set_reminder_skill.execute(
        task="Second test reminder - this should trigger in 1 minute",
        time="in 1 minute"
    )
    
    if result2.success:
        logger.info(f"✓ Reminder created: {result2.result['reminder_id']}")
        logger.info(f"  Task: {result2.result['task']}")
        logger.info(f"  Scheduled: {result2.result['scheduled_time_human']}")
    else:
        logger.error(f"✗ Failed to create reminder: {result2.error_message}")
    
    # Reminder 3: In 2 minutes
    logger.info("\n3. Creating reminder for 2 minutes from now...")
    result3 = set_reminder_skill.execute(
        task="Third test reminder - this should trigger in 2 minutes",
        time="in 2 minutes"
    )
    
    if result3.success:
        logger.info(f"✓ Reminder created: {result3.result['reminder_id']}")
        logger.info(f"  Task: {result3.result['task']}")
        logger.info(f"  Scheduled: {result3.result['scheduled_time_human']}")
    else:
        logger.error(f"✗ Failed to create reminder: {result3.error_message}")
    
    # Monitor for reminders
    logger.info("\n" + "="*60)
    logger.info("MONITORING: Waiting for reminders to trigger...")
    logger.info("The reminder delivery hook checks every 60 seconds")
    logger.info("Press Ctrl+C to stop")
    logger.info("="*60 + "\n")
    
    try:
        # Keep the script running to allow hooks to execute
        # The hooks engine runs in background threads
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("\n\nStopping demo...")
        hooks_engine.shutdown()
        logger.info("Hooks engine shut down")
        logger.info("Demo completed")


if __name__ == "__main__":
    main()
