"""Demo script for testing the Morning Brief Hook implementation.

This script demonstrates:
1. Creating a HooksEngine
2. Creating a MorningBriefHook
3. Registering the hook with a cron schedule
4. Manually executing the hook for testing
"""

import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main demo function."""
    logger.info("=== Morning Brief Hook Demo ===")
    
    # Import required modules
    from jarvis.hooks import HooksEngine, create_morning_brief_hook
    from jarvis.skills import SkillRegistry
    from jarvis.skills.daily_brief import DailyBriefSkill
    from jarvis.voice.voice_interface import VoiceInterface
    from jarvis.memory.memory_system import MemorySystem
    from jarvis.config import load_config
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        
        # Initialize components
        logger.info("Initializing components...")
        
        # Initialize Memory System
        memory_system = MemorySystem(
            supabase_url=config.supabase_url,
            supabase_key=config.supabase_key
        )
        
        # Initialize Skill Registry
        skill_registry = SkillRegistry()
        
        # Register daily_brief skill
        daily_brief_skill = DailyBriefSkill(skill_registry=skill_registry)
        skill_registry.register_skill(daily_brief_skill)
        logger.info("Registered daily_brief skill")
        
        # Initialize Voice Interface (if TTS is configured)
        voice_interface = None
        if config.tts_api_key:
            try:
                voice_interface = VoiceInterface(
                    model_name=config.stt_model,
                    elevenlabs_api_key=config.tts_api_key
                )
                logger.info("Voice interface initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize voice interface: {e}")
                logger.info("Will use text fallback for morning brief")
        else:
            logger.info("TTS API key not configured, will use text fallback")
        
        # Initialize Hooks Engine
        logger.info("Initializing hooks engine...")
        hooks_engine = HooksEngine()
        
        # Create and register morning brief hook
        logger.info("Creating morning brief hook...")
        morning_brief = create_morning_brief_hook(
            hooks_engine=hooks_engine,
            skill_registry=skill_registry,
            voice_interface=voice_interface,
            memory_system=memory_system
        )
        
        # Display hook information
        hook = hooks_engine.get_hook("morning_brief")
        if hook:
            logger.info(f"Hook registered successfully:")
            logger.info(f"  ID: {hook.id}")
            logger.info(f"  Name: {hook.name}")
            logger.info(f"  Description: {hook.description}")
            logger.info(f"  Type: {hook.hook_type}")
            logger.info(f"  Trigger: {hook.trigger}")
            logger.info(f"  Enabled: {hook.enabled}")
        
        # List all active hooks
        active_hooks = hooks_engine.list_active_hooks()
        logger.info(f"\nActive hooks: {len(active_hooks)}")
        for h in active_hooks:
            logger.info(f"  - {h.name} ({h.id})")
        
        # Manual execution for testing
        logger.info("\n=== Testing Manual Execution ===")
        logger.info("Manually executing morning brief hook...")
        hooks_engine.execute_hook("morning_brief")
        
        logger.info("\n=== Demo Complete ===")
        logger.info("The morning brief hook is now scheduled and will run automatically")
        logger.info("at the configured time (default: 7:00 AM daily)")
        logger.info("\nTo change the time, update the 'morning_brief_time' preference")
        logger.info("in the personal_profile table (format: 'HH:MM' or cron expression)")
        
        # Keep the scheduler running for a bit to show it's working
        logger.info("\nScheduler is running. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nShutting down...")
            hooks_engine.shutdown()
            logger.info("Hooks engine shutdown complete")
    
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
