"""Reminder Delivery Hook for JARVIS - Automated reminder delivery.

Validates: Requirements 12.3
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ReminderDeliveryHook:
    """
    Reminder delivery hook that checks for due reminders every minute.
    
    Queries the reminders table for undelivered reminders where reminder_time <= now,
    delivers voice alerts using TTS, and marks reminders as delivered in the database.
    
    Validates: Requirements 12.3
    """
    
    def __init__(
        self,
        voice_interface,
        memory_system,
        user_id: str = "default_user"
    ):
        """
        Initialize the reminder delivery hook.
        
        Args:
            voice_interface: VoiceInterface instance for TTS delivery
            memory_system: MemorySystem instance for database access
            user_id: User ID for retrieving preferences (default: "default_user")
        """
        self._voice_interface = voice_interface
        self._memory_system = memory_system
        self._user_id = user_id
        
        logger.info("ReminderDeliveryHook initialized")
    
    def execute(self) -> None:
        """
        Execute the reminder delivery hook.
        
        Steps:
        1. Query reminders table for undelivered reminders where reminder_time <= now
        2. For each reminder:
           - Create reminder message with task description
           - Use VoiceInterface to deliver the reminder via TTS
           - Mark the reminder as delivered in the database (set delivered=true)
        3. Handle errors gracefully (if TTS fails, log error but still mark as delivered)
        
        Validates: Requirements 12.3
        """
        try:
            logger.debug("Executing reminder delivery hook...")
            
            # Step 1: Query for due reminders
            if not self._memory_system:
                logger.error("Memory system not available")
                return
            
            due_reminders = self._get_due_reminders()
            
            if not due_reminders:
                logger.debug("No due reminders found")
                return
            
            logger.info(f"Found {len(due_reminders)} due reminder(s)")
            
            # Step 2: Deliver each reminder
            for reminder in due_reminders:
                reminder_id = reminder.get("id")
                task = reminder.get("task", "")
                scheduled_time = reminder.get("scheduled_time")
                
                if not reminder_id or not task:
                    logger.warning(f"Invalid reminder data: {reminder}")
                    continue
                
                logger.info(f"Delivering reminder: {task}")
                
                # Deliver the reminder via TTS
                delivery_success = self._deliver_reminder(task, scheduled_time)
                
                # Mark as delivered regardless of TTS success
                # (if TTS fails, we still don't want to retry indefinitely)
                self._mark_reminder_delivered(reminder_id)
                
                if delivery_success:
                    logger.info(f"Reminder delivered successfully: {task}")
                else:
                    logger.warning(f"Reminder marked as delivered but TTS failed: {task}")
        
        except Exception as e:
            logger.error(f"Reminder delivery hook execution failed: {e}", exc_info=True)
    
    def _get_due_reminders(self) -> List[Dict[str, Any]]:
        """
        Query the reminders table for undelivered reminders where reminder_time <= now.
        
        Returns:
            List of reminder dictionaries with id, task, scheduled_time
        """
        try:
            # Query reminders table
            # SELECT * FROM reminders WHERE delivered = FALSE AND scheduled_time <= NOW()
            now = datetime.now()
            
            result = self._memory_system.client.table("reminders").select(
                "id, task, scheduled_time"
            ).eq("delivered", False).lte("scheduled_time", now.isoformat()).execute()
            
            if not result.data:
                return []
            
            logger.debug(f"Retrieved {len(result.data)} due reminder(s) from database")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to query due reminders: {e}", exc_info=True)
            return []
    
    def _deliver_reminder(
        self,
        task: str,
        scheduled_time: Optional[str]
    ) -> bool:
        """
        Deliver a voice reminder for a task.
        
        Args:
            task: Reminder task description
            scheduled_time: Scheduled time (ISO format string)
            
        Returns:
            True if delivery succeeded, False otherwise
        """
        try:
            # Create reminder message
            reminder_message = f"Reminder: {task}"
            
            # Add time context if available
            if scheduled_time:
                try:
                    scheduled_dt = datetime.fromisoformat(scheduled_time.replace("Z", "+00:00"))
                    time_str = scheduled_dt.strftime("%I:%M %p")
                    reminder_message = f"Reminder for {time_str}: {task}"
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Failed to parse scheduled time '{scheduled_time}': {e}")
            
            logger.info(f"Delivering reminder: {reminder_message}")
            
            # Deliver via TTS
            if not self._voice_interface:
                logger.error("Voice interface not available")
                # Fall back to logging the reminder
                logger.info(f"Reminder (text fallback):\n{reminder_message}")
                return False
            
            try:
                # Convert to speech
                audio_bytes = self._voice_interface.text_to_speech(reminder_message)
                
                if not audio_bytes:
                    logger.warning("TTS returned empty audio")
                    return False
                
                logger.debug(f"TTS conversion successful ({len(audio_bytes)} bytes)")
                
                # Play the audio
                self._voice_interface.play_audio(audio_bytes)
                logger.info(f"Reminder delivered successfully via TTS")
                return True
                
            except Exception as tts_error:
                logger.error(f"TTS/playback failed: {tts_error}")
                # Fall back to logging the reminder
                logger.info(f"Reminder (text fallback):\n{reminder_message}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to deliver reminder: {e}", exc_info=True)
            return False
    
    def _mark_reminder_delivered(self, reminder_id: str) -> None:
        """
        Mark a reminder as delivered in the database.
        
        Updates the reminders table to set delivered=true and delivered_at=now.
        
        Args:
            reminder_id: UUID of the reminder to mark as delivered
        """
        try:
            now = datetime.now()
            
            # UPDATE reminders SET delivered = TRUE, delivered_at = NOW() WHERE id = reminder_id
            result = self._memory_system.client.table("reminders").update({
                "delivered": True,
                "delivered_at": now.isoformat()
            }).eq("id", reminder_id).execute()
            
            if not result.data:
                logger.warning(f"Failed to mark reminder as delivered: {reminder_id}")
            else:
                logger.debug(f"Marked reminder as delivered: {reminder_id}")
            
        except Exception as e:
            logger.error(f"Failed to mark reminder as delivered: {e}", exc_info=True)


def create_reminder_delivery_hook(
    hooks_engine,
    voice_interface,
    memory_system,
    user_id: str = "default_user"
):
    """
    Create and register the reminder delivery hook with the hooks engine.
    
    Args:
        hooks_engine: HooksEngine instance to register the hook with
        voice_interface: VoiceInterface instance for TTS delivery
        memory_system: MemorySystem instance for database access
        user_id: User ID for retrieving preferences (default: "default_user")
        
    Returns:
        The created ReminderDeliveryHook instance
        
    Validates: Requirements 12.3
    """
    from jarvis.hooks.hooks_engine import Hook
    
    # Create the reminder delivery hook instance
    reminder_delivery = ReminderDeliveryHook(
        voice_interface=voice_interface,
        memory_system=memory_system,
        user_id=user_id
    )
    
    # Create the hook as an interval-based hook (every 1 minute = 60 seconds)
    hook = Hook(
        id="reminder_delivery",
        name="Reminder Delivery",
        description="Checks for due reminders every minute and delivers voice alerts via TTS",
        hook_type="interval",
        trigger="60",  # 60 seconds = 1 minute
        callback=reminder_delivery.execute,
        enabled=True
    )
    
    # Register with hooks engine
    hooks_engine.register_hook(hook)
    
    logger.info(
        "Reminder delivery hook registered with 1-minute interval"
    )
    
    return reminder_delivery
