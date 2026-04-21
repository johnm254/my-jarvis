"""Calendar Reminder Hook for JARVIS - Automated calendar event reminders.

Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5
"""

import logging
from typing import Optional, Set, Dict, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class CalendarReminderHook:
    """
    Calendar reminder hook that checks calendar every 5 minutes.
    
    Retrieves upcoming events within 15 minutes and delivers voice reminders
    with event title, time, and context. Tracks delivered reminders to avoid
    duplicates.
    
    Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5
    """
    
    def __init__(
        self,
        skill_registry,
        voice_interface,
        memory_system,
        user_id: str = "default_user"
    ):
        """
        Initialize the calendar reminder hook.
        
        Args:
            skill_registry: SkillRegistry instance for calling manage_calendar skill
            voice_interface: VoiceInterface instance for TTS delivery
            memory_system: MemorySystem instance for tracking delivered reminders
            user_id: User ID for retrieving preferences (default: "default_user")
        """
        self._skill_registry = skill_registry
        self._voice_interface = voice_interface
        self._memory_system = memory_system
        self._user_id = user_id
        
        # In-memory set to track delivered reminders (event_id + start_time)
        # This prevents duplicate reminders for the same event
        self._delivered_reminders: Set[str] = set()
        
        logger.info("CalendarReminderHook initialized")
    
    def execute(self) -> None:
        """
        Execute the calendar reminder hook.
        
        Steps:
        1. Call ManageCalendarSkill with action="read" to get upcoming events
        2. Filter events that are within 15 minutes
        3. For each event not yet reminded:
           - Create reminder message with event title, time, and context
           - Use VoiceInterface to deliver the reminder via TTS
           - Mark the event as reminded
        4. Handle errors gracefully
        
        Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5
        """
        try:
            logger.debug("Executing calendar reminder hook...")
            
            # Step 1: Get the manage_calendar skill
            if not self._skill_registry:
                logger.error("Skill registry not available")
                return
            
            manage_calendar_skill = self._skill_registry.get_skill("manage_calendar")
            if not manage_calendar_skill:
                logger.error("Manage calendar skill not found")
                return
            
            # Step 2: Retrieve upcoming events
            # Request events for the next day to ensure we capture all within 15 minutes
            logger.debug("Retrieving upcoming calendar events...")
            result = manage_calendar_skill.execute(
                action="read",
                details={"days_ahead": 1}
            )
            
            if not result.success:
                logger.error(f"Failed to retrieve calendar events: {result.error_message}")
                return
            
            events = result.result.get("events", [])
            if not events:
                logger.debug("No upcoming events found")
                return
            
            logger.debug(f"Retrieved {len(events)} upcoming events")
            
            # Step 3: Filter events within 15 minutes
            now = datetime.now()
            reminder_window = timedelta(minutes=15)
            
            upcoming_events = []
            for event in events:
                event_start = self._parse_event_time(event.get("start_time"))
                if not event_start:
                    logger.warning(f"Could not parse start time for event: {event.get('title')}")
                    continue
                
                # Calculate time until event
                time_until_event = event_start - now
                
                # Check if event is within 15 minutes and hasn't started yet
                if timedelta(0) <= time_until_event <= reminder_window:
                    upcoming_events.append({
                        "event": event,
                        "start_time": event_start,
                        "time_until": time_until_event
                    })
            
            if not upcoming_events:
                logger.debug("No events within 15-minute reminder window")
                return
            
            logger.info(f"Found {len(upcoming_events)} events within 15-minute window")
            
            # Step 4: Deliver reminders for events not yet reminded
            for item in upcoming_events:
                event = item["event"]
                start_time = item["start_time"]
                time_until = item["time_until"]
                
                # Create unique reminder key (event_id only, not including exact timestamp)
                # This prevents duplicate reminders for the same event
                event_id = event.get("id", event.get("title", "unknown"))
                # Use date + event_id to allow reminders for recurring events on different days
                event_date = start_time.strftime("%Y-%m-%d")
                reminder_key = f"{event_id}_{event_date}"
                
                # Check if we've already delivered this reminder
                if reminder_key in self._delivered_reminders:
                    logger.debug(f"Reminder already delivered for: {event.get('title')}")
                    continue
                
                # Deliver the reminder
                self._deliver_reminder(event, start_time, time_until)
                
                # Mark as delivered
                self._delivered_reminders.add(reminder_key)
                
                # Store in memory system for persistence across restarts
                self._store_delivered_reminder(reminder_key, event)
            
        except Exception as e:
            logger.error(f"Calendar reminder hook execution failed: {e}", exc_info=True)
    
    def _parse_event_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """
        Parse event time string to datetime object.
        
        Args:
            time_str: Time string in ISO format
            
        Returns:
            datetime object or None if parsing fails
        """
        if not time_str:
            return None
        
        try:
            # Handle ISO format with timezone
            if time_str.endswith("Z"):
                time_str = time_str.replace("Z", "+00:00")
            
            return datetime.fromisoformat(time_str)
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse time '{time_str}': {e}")
            return None
    
    def _deliver_reminder(
        self,
        event: Dict[str, Any],
        start_time: datetime,
        time_until: timedelta
    ) -> None:
        """
        Deliver a voice reminder for an event.
        
        Args:
            event: Event dictionary with title, description, location, etc.
            start_time: Event start time as datetime
            time_until: Time until event starts
        """
        try:
            # Extract event details
            title = event.get("title", "Untitled Event")
            description = event.get("description", "")
            location = event.get("location", "")
            
            # Format time until event
            minutes_until = int(time_until.total_seconds() / 60)
            
            # Create reminder message
            reminder_parts = [
                f"Reminder: You have '{title}' in {minutes_until} minutes"
            ]
            
            # Add time
            time_str = start_time.strftime("%I:%M %p")
            reminder_parts.append(f"at {time_str}")
            
            # Add location if available
            if location:
                reminder_parts.append(f"at {location}")
            
            # Add description/context if available
            if description:
                # Limit description to first 100 characters for brevity
                desc_preview = description[:100]
                if len(description) > 100:
                    desc_preview += "..."
                reminder_parts.append(f"Details: {desc_preview}")
            
            reminder_message = ". ".join(reminder_parts) + "."
            
            logger.info(f"Delivering reminder: {title} in {minutes_until} minutes")
            
            # Deliver via TTS
            if not self._voice_interface:
                logger.error("Voice interface not available")
                # Fall back to logging the reminder
                logger.info(f"Calendar Reminder (text fallback):\n{reminder_message}")
                return
            
            try:
                # Convert to speech
                audio_bytes = self._voice_interface.text_to_speech(reminder_message)
                
                if not audio_bytes:
                    logger.warning("TTS returned empty audio")
                    return
                
                logger.debug(f"TTS conversion successful ({len(audio_bytes)} bytes)")
                
                # Play the audio
                self._voice_interface.play_audio(audio_bytes)
                logger.info(f"Reminder delivered successfully for: {title}")
                
            except Exception as tts_error:
                logger.error(f"TTS/playback failed: {tts_error}")
                # Fall back to logging the reminder
                logger.info(f"Calendar Reminder (text fallback):\n{reminder_message}")
        
        except Exception as e:
            logger.error(f"Failed to deliver reminder: {e}", exc_info=True)
    
    def _store_delivered_reminder(
        self,
        reminder_key: str,
        event: Dict[str, Any]
    ) -> None:
        """
        Store delivered reminder in memory system for persistence.
        
        This allows the system to remember delivered reminders across restarts
        and avoid duplicate notifications.
        
        Args:
            reminder_key: Unique key for the reminder
            event: Event dictionary
        """
        try:
            if not self._memory_system:
                logger.warning("Memory system not available, cannot persist reminder")
                return
            
            # Store as a preference with timestamp
            preference_key = f"delivered_reminder_{reminder_key}"
            preference_value = {
                "event_title": event.get("title", "Unknown"),
                "delivered_at": datetime.now().isoformat(),
                "event_start": event.get("start_time", "")
            }
            
            self._memory_system.update_preference(
                self._user_id,
                preference_key,
                preference_value
            )
            
            logger.debug(f"Stored delivered reminder: {reminder_key}")
            
        except Exception as e:
            logger.error(f"Failed to store delivered reminder: {e}", exc_info=True)
    
    def load_delivered_reminders(self) -> None:
        """
        Load previously delivered reminders from memory system.
        
        This should be called on initialization to restore state after restart.
        Only loads reminders from the last 24 hours to avoid memory bloat.
        """
        try:
            if not self._memory_system:
                logger.warning("Memory system not available, cannot load reminders")
                return
            
            # Get user profile with preferences
            profile = self._memory_system.get_personal_profile(self._user_id)
            
            if not profile or not profile.preferences:
                logger.debug("No preferences found, starting with empty reminder set")
                return
            
            # Filter preferences for delivered reminders from last 24 hours
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for key, value in profile.preferences.items():
                if key.startswith("delivered_reminder_"):
                    # Extract reminder key
                    reminder_key = key.replace("delivered_reminder_", "")
                    
                    # Check if reminder is recent (within last 24 hours)
                    if isinstance(value, dict):
                        delivered_at_str = value.get("delivered_at")
                        if delivered_at_str:
                            try:
                                delivered_at = datetime.fromisoformat(delivered_at_str)
                                if delivered_at >= cutoff_time:
                                    self._delivered_reminders.add(reminder_key)
                                    logger.debug(f"Loaded delivered reminder: {reminder_key}")
                            except (ValueError, AttributeError):
                                logger.warning(f"Invalid delivered_at format: {delivered_at_str}")
            
            logger.info(f"Loaded {len(self._delivered_reminders)} delivered reminders from memory")
            
        except Exception as e:
            logger.error(f"Failed to load delivered reminders: {e}", exc_info=True)


def create_calendar_reminder_hook(
    hooks_engine,
    skill_registry,
    voice_interface,
    memory_system,
    user_id: str = "default_user"
):
    """
    Create and register the calendar reminder hook with the hooks engine.
    
    Args:
        hooks_engine: HooksEngine instance to register the hook with
        skill_registry: SkillRegistry instance for calling manage_calendar skill
        voice_interface: VoiceInterface instance for TTS delivery
        memory_system: MemorySystem instance for tracking delivered reminders
        user_id: User ID for retrieving preferences (default: "default_user")
        
    Returns:
        The created CalendarReminderHook instance
        
    Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5
    """
    from jarvis.hooks.hooks_engine import Hook
    
    # Create the calendar reminder hook instance
    calendar_reminder = CalendarReminderHook(
        skill_registry=skill_registry,
        voice_interface=voice_interface,
        memory_system=memory_system,
        user_id=user_id
    )
    
    # Load previously delivered reminders from memory
    calendar_reminder.load_delivered_reminders()
    
    # Create the hook as an interval-based hook (every 5 minutes = 300 seconds)
    hook = Hook(
        id="calendar_reminder",
        name="Calendar Reminder",
        description="Checks calendar every 5 minutes and delivers voice reminders for events within 15 minutes",
        hook_type="interval",
        trigger="300",  # 300 seconds = 5 minutes
        callback=calendar_reminder.execute,
        enabled=True
    )
    
    # Register with hooks engine
    hooks_engine.register_hook(hook)
    
    logger.info(
        "Calendar reminder hook registered with 5-minute interval"
    )
    
    return calendar_reminder
