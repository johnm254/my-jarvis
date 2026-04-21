"""Morning Brief Hook for JARVIS - Automated daily brief delivery.

Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5
"""

import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MorningBriefHook:
    """
    Morning brief hook that executes daily_brief at a configured time.
    
    Delivers the brief via TTS for voice output.
    Time is configurable via Dashboard settings (stored in personal_profile).
    
    Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5
    """
    
    def __init__(
        self,
        skill_registry,
        voice_interface,
        memory_system,
        user_id: str = "default_user"
    ):
        """
        Initialize the morning brief hook.
        
        Args:
            skill_registry: SkillRegistry instance for calling daily_brief skill
            voice_interface: VoiceInterface instance for TTS delivery
            memory_system: MemorySystem instance for reading user preferences
            user_id: User ID for retrieving preferences (default: "default_user")
        """
        self._skill_registry = skill_registry
        self._voice_interface = voice_interface
        self._memory_system = memory_system
        self._user_id = user_id
        
        logger.info("MorningBriefHook initialized")
    
    def execute(self) -> None:
        """
        Execute the morning brief hook.
        
        Steps:
        1. Call DailyBriefSkill to get the brief content
        2. Use VoiceInterface.text_to_speech() to convert to audio
        3. Use VoiceInterface.play_audio() to deliver via TTS
        4. Handle errors gracefully
        
        Validates: Requirements 14.1, 14.2, 14.3
        """
        try:
            logger.info("Executing morning brief hook...")
            
            # Step 1: Get the daily brief skill
            if not self._skill_registry:
                logger.error("Skill registry not available")
                return
            
            daily_brief_skill = self._skill_registry.get_skill("daily_brief")
            if not daily_brief_skill:
                logger.error("Daily brief skill not found")
                return
            
            # Step 2: Execute the daily brief skill
            logger.info("Calling daily_brief skill...")
            result = daily_brief_skill.execute()
            
            if not result.success:
                logger.error(f"Daily brief skill failed: {result.error_message}")
                return
            
            # Get the summary text
            summary = result.result.get("summary", "")
            if not summary:
                logger.warning("Daily brief returned empty summary")
                return
            
            logger.info(f"Daily brief generated successfully ({len(summary)} chars)")
            
            # Step 3: Convert to speech using TTS
            if not self._voice_interface:
                logger.error("Voice interface not available")
                # Fall back to logging the brief
                logger.info(f"Morning Brief (text fallback):\n{summary}")
                return
            
            try:
                logger.info("Converting brief to speech...")
                audio_bytes = self._voice_interface.text_to_speech(summary)
                
                if not audio_bytes:
                    logger.warning("TTS returned empty audio")
                    return
                
                logger.info(f"TTS conversion successful ({len(audio_bytes)} bytes)")
                
            except Exception as tts_error:
                logger.error(f"TTS conversion failed: {tts_error}")
                # Fall back to logging the brief
                logger.info(f"Morning Brief (text fallback):\n{summary}")
                return
            
            # Step 4: Play the audio
            try:
                logger.info("Playing morning brief audio...")
                self._voice_interface.play_audio(audio_bytes)
                logger.info("Morning brief delivered successfully via TTS")
                
            except Exception as playback_error:
                logger.error(f"Audio playback failed: {playback_error}")
                # Fall back to logging the brief
                logger.info(f"Morning Brief (text fallback):\n{summary}")
        
        except Exception as e:
            logger.error(f"Morning brief hook execution failed: {e}", exc_info=True)
    
    def get_configured_time(self) -> str:
        """
        Get the configured morning brief time from user preferences.
        
        Returns:
            Cron expression for the configured time (default: "0 7 * * *" = 7:00 AM)
            
        Validates: Requirement 14.5
        """
        try:
            if not self._memory_system:
                logger.warning("Memory system not available, using default time")
                return "0 7 * * *"
            
            # Get user profile
            profile = self._memory_system.get_personal_profile(self._user_id)
            
            if not profile:
                logger.warning("User profile not found, using default time")
                return "0 7 * * *"
            
            # Check if morning_brief_time is configured in preferences
            preferences = profile.preferences or {}
            morning_brief_time = preferences.get("morning_brief_time")
            
            if not morning_brief_time:
                logger.info("Morning brief time not configured, using default (7:00 AM)")
                return "0 7 * * *"
            
            # Parse the time (expected format: "HH:MM" or cron expression)
            if isinstance(morning_brief_time, str):
                # If it's already a cron expression (5 parts), use it directly
                if len(morning_brief_time.split()) == 5:
                    logger.info(f"Using configured cron expression: {morning_brief_time}")
                    return morning_brief_time
                
                # Otherwise, assume it's "HH:MM" format
                try:
                    time_parts = morning_brief_time.split(":")
                    if len(time_parts) == 2:
                        hour = int(time_parts[0])
                        minute = int(time_parts[1])
                        
                        # Validate hour and minute
                        if 0 <= hour <= 23 and 0 <= minute <= 59:
                            cron_expr = f"{minute} {hour} * * *"
                            logger.info(
                                f"Using configured time: {morning_brief_time} "
                                f"(cron: {cron_expr})"
                            )
                            return cron_expr
                        else:
                            logger.warning(
                                f"Invalid time values: {morning_brief_time}, "
                                f"using default"
                            )
                            return "0 7 * * *"
                    else:
                        logger.warning(
                            f"Invalid time format: {morning_brief_time}, "
                            f"expected HH:MM or cron expression"
                        )
                        return "0 7 * * *"
                        
                except (ValueError, IndexError) as e:
                    logger.warning(
                        f"Failed to parse time '{morning_brief_time}': {e}, "
                        f"using default"
                    )
                    return "0 7 * * *"
            else:
                logger.warning(
                    f"Invalid morning_brief_time type: {type(morning_brief_time)}, "
                    f"using default"
                )
                return "0 7 * * *"
        
        except Exception as e:
            logger.error(f"Failed to get configured time: {e}", exc_info=True)
            return "0 7 * * *"


def create_morning_brief_hook(
    hooks_engine,
    skill_registry,
    voice_interface,
    memory_system,
    user_id: str = "default_user"
):
    """
    Create and register the morning brief hook with the hooks engine.
    
    Args:
        hooks_engine: HooksEngine instance to register the hook with
        skill_registry: SkillRegistry instance for calling daily_brief skill
        voice_interface: VoiceInterface instance for TTS delivery
        memory_system: MemorySystem instance for reading user preferences
        user_id: User ID for retrieving preferences (default: "default_user")
        
    Returns:
        The created MorningBriefHook instance
        
    Validates: Requirements 14.1, 14.2, 14.4, 14.5
    """
    from jarvis.hooks.hooks_engine import Hook
    
    # Create the morning brief hook instance
    morning_brief = MorningBriefHook(
        skill_registry=skill_registry,
        voice_interface=voice_interface,
        memory_system=memory_system,
        user_id=user_id
    )
    
    # Get the configured time (or default to 7:00 AM)
    cron_expression = morning_brief.get_configured_time()
    
    # Create the hook
    hook = Hook(
        id="morning_brief",
        name="Morning Brief",
        description="Automated daily brief delivered via TTS at configured time",
        hook_type="cron",
        trigger=cron_expression,
        callback=morning_brief.execute,
        enabled=True
    )
    
    # Register with hooks engine
    hooks_engine.register_hook(hook)
    
    logger.info(
        f"Morning brief hook registered with schedule: {cron_expression}"
    )
    
    return morning_brief
