"""Set Reminder Skill for JARVIS with natural language time parsing.

Validates: Requirements 12.1, 12.2, 12.4, 12.5
"""

import time
import re
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from dateutil import parser as dateutil_parser

from jarvis.skills.base import Skill, SkillResult


class SetReminderSkill(Skill):
    """
    Set reminder skill with natural language time parsing.
    
    Parses natural language time expressions and creates scheduled reminders.
    Stores reminders in Memory System for persistence.
    
    Validates: Requirements 12.1, 12.2, 12.4, 12.5
    """
    
    def __init__(self, memory_system=None):
        """
        Initialize the set reminder skill.
        
        Args:
            memory_system: MemorySystem instance for storing reminders
        """
        super().__init__()
        self._name = "set_reminder"
        self._description = "Set a reminder with natural language time parsing. Supports expressions like 'in 30 minutes', 'tomorrow at 9am', 'next Monday at 2pm'."
        self._parameters = {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The task or message for the reminder"
                },
                "time": {
                    "type": "string",
                    "description": "When to deliver the reminder. Supports natural language like 'in 30 minutes', 'tomorrow at 9am', 'next Monday'"
                }
            },
            "required": ["task", "time"]
        }
        
        self._memory_system = memory_system
    
    def _parse_relative_time(self, time_str: str, now: datetime) -> Optional[datetime]:
        """
        Parse relative time expressions like "in 30 minutes", "in 2 hours", "in 3 days".
        
        Args:
            time_str: Time string to parse
            now: Current datetime
            
        Returns:
            Parsed datetime or None if not a relative time expression
        """
        time_str_lower = time_str.lower().strip()
        
        # Pattern: "in X minutes/hours/days/weeks"
        pattern = r'^in\s+(\d+)\s+(minute|minutes|hour|hours|day|days|week|weeks)$'
        match = re.match(pattern, time_str_lower)
        
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            
            if unit.startswith('minute'):
                return now + timedelta(minutes=amount)
            elif unit.startswith('hour'):
                return now + timedelta(hours=amount)
            elif unit.startswith('day'):
                return now + timedelta(days=amount)
            elif unit.startswith('week'):
                return now + timedelta(weeks=amount)
        
        return None
    
    def _parse_tomorrow_time(self, time_str: str, now: datetime) -> Optional[datetime]:
        """
        Parse "tomorrow" expressions like "tomorrow", "tomorrow at 9am", "tomorrow at 14:30".
        
        Args:
            time_str: Time string to parse
            now: Current datetime
            
        Returns:
            Parsed datetime or None if not a tomorrow expression
        """
        time_str_lower = time_str.lower().strip()
        
        if not time_str_lower.startswith('tomorrow'):
            return None
        
        # Base tomorrow date
        tomorrow = now + timedelta(days=1)
        
        # Check if there's a time specified
        if time_str_lower == 'tomorrow':
            # Default to 9am tomorrow
            return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Extract time part after "tomorrow at"
        if ' at ' in time_str_lower:
            time_part = time_str_lower.split(' at ', 1)[1].strip()
            
            try:
                # Parse the time part
                parsed_time = dateutil_parser.parse(time_part, default=tomorrow)
                # Combine tomorrow's date with parsed time
                return tomorrow.replace(
                    hour=parsed_time.hour,
                    minute=parsed_time.minute,
                    second=0,
                    microsecond=0
                )
            except (ValueError, dateutil_parser.ParserError):
                return None
        
        return None
    
    def _parse_next_weekday(self, time_str: str, now: datetime) -> Optional[datetime]:
        """
        Parse "next [weekday]" expressions like "next Monday", "next Friday at 2pm".
        
        Args:
            time_str: Time string to parse
            now: Current datetime
            
        Returns:
            Parsed datetime or None if not a next weekday expression
        """
        time_str_lower = time_str.lower().strip()
        
        if not time_str_lower.startswith('next '):
            return None
        
        weekdays = {
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5,
            'sunday': 6
        }
        
        # Extract weekday and optional time
        parts = time_str_lower.split(' at ', 1)
        weekday_part = parts[0].replace('next ', '').strip()
        time_part = parts[1].strip() if len(parts) > 1 else None
        
        # Find the weekday
        target_weekday = None
        for day_name, day_num in weekdays.items():
            if weekday_part == day_name:
                target_weekday = day_num
                break
        
        if target_weekday is None:
            return None
        
        # Calculate next occurrence of this weekday
        current_weekday = now.weekday()
        days_ahead = target_weekday - current_weekday
        
        # If the target day is today or earlier in the week, go to next week
        if days_ahead <= 0:
            days_ahead += 7
        
        target_date = now + timedelta(days=days_ahead)
        
        # Parse time if provided
        if time_part:
            try:
                parsed_time = dateutil_parser.parse(time_part, default=target_date)
                return target_date.replace(
                    hour=parsed_time.hour,
                    minute=parsed_time.minute,
                    second=0,
                    microsecond=0
                )
            except (ValueError, dateutil_parser.ParserError):
                return None
        else:
            # Default to 9am
            return target_date.replace(hour=9, minute=0, second=0, microsecond=0)
    
    def _parse_absolute_time(self, time_str: str, now: datetime) -> Optional[datetime]:
        """
        Parse absolute time expressions using dateutil parser.
        
        Args:
            time_str: Time string to parse
            now: Current datetime
            
        Returns:
            Parsed datetime or None if parsing fails
        """
        try:
            # Use dateutil parser for flexible parsing
            parsed = dateutil_parser.parse(time_str, default=now, fuzzy=True)
            
            # If parsed time is in the past, assume it's for tomorrow
            if parsed < now:
                parsed = parsed + timedelta(days=1)
            
            return parsed
        except (ValueError, dateutil_parser.ParserError):
            return None
    
    def parse_time_expression(self, time_str: str) -> tuple[bool, Optional[datetime], Optional[str]]:
        """
        Parse natural language time expression into datetime.
        
        Supports:
        - Relative: "in 30 minutes", "in 2 hours", "in 3 days"
        - Tomorrow: "tomorrow", "tomorrow at 9am"
        - Next weekday: "next Monday", "next Friday at 2pm"
        - Absolute: "2024-01-15 10:00", "January 15 at 10am"
        
        Args:
            time_str: Time expression to parse
            
        Returns:
            Tuple of (success, parsed_datetime, error_message)
            
        Validates: Requirements 12.4
        """
        now = datetime.now()
        
        # Try relative time parsing
        parsed = self._parse_relative_time(time_str, now)
        if parsed:
            return True, parsed, None
        
        # Try tomorrow parsing
        parsed = self._parse_tomorrow_time(time_str, now)
        if parsed:
            return True, parsed, None
        
        # Try next weekday parsing
        parsed = self._parse_next_weekday(time_str, now)
        if parsed:
            return True, parsed, None
        
        # Try absolute time parsing
        parsed = self._parse_absolute_time(time_str, now)
        if parsed:
            return True, parsed, None
        
        # Parsing failed
        return False, None, f"Could not parse time expression: '{time_str}'. Try formats like 'in 30 minutes', 'tomorrow at 9am', or 'next Monday'."
    
    def _store_reminder(
        self,
        task: str,
        scheduled_time: datetime
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Store reminder in Memory System.
        
        Args:
            task: Reminder task
            scheduled_time: When to deliver the reminder
            
        Returns:
            Tuple of (success, reminder_id, error_message)
        """
        if not self._memory_system:
            return False, None, "Memory System not available. Cannot store reminder."
        
        try:
            # Insert into reminders table with task, scheduled_time, delivered=False
            reminder_data = {
                "task": task,
                "scheduled_time": scheduled_time.isoformat(),
                "delivered": False
            }
            
            result = self._memory_system.client.table("reminders").insert(reminder_data).execute()
            
            if not result.data or len(result.data) == 0:
                return False, None, "Failed to store reminder in database"
            
            # Extract the reminder ID from the result
            reminder_id = result.data[0].get("id")
            
            if not reminder_id:
                return False, None, "Reminder stored but ID not returned"
            
            return True, reminder_id, None
            
        except Exception as e:
            error_msg = f"Failed to store reminder: {e}"
            return False, None, error_msg
    
    def execute(self, **kwargs) -> SkillResult:
        """
        Execute reminder creation.
        
        Args:
            **kwargs: Must contain 'task' and 'time' parameters
            
        Returns:
            SkillResult with reminder details
            
        Validates: Requirements 12.1, 12.2, 12.4, 12.5
        """
        start_time = time.time()
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(**kwargs)
        if not is_valid:
            return SkillResult(
                success=False,
                result=None,
                error_message=error_msg,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        task = kwargs.get("task")
        time_str = kwargs.get("time")
        
        # Parse time expression (requirement 12.4)
        parse_success, scheduled_time, parse_error = self.parse_time_expression(time_str)
        
        if not parse_success:
            return SkillResult(
                success=False,
                result=None,
                error_message=parse_error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Validate that scheduled time is in the future
        if scheduled_time <= datetime.now():
            return SkillResult(
                success=False,
                result=None,
                error_message=f"Scheduled time must be in the future. Parsed time: {scheduled_time.isoformat()}",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Store reminder in Memory System (requirement 12.5)
        store_success, reminder_id, store_error = self._store_reminder(task, scheduled_time)
        
        if not store_success:
            return SkillResult(
                success=False,
                result=None,
                error_message=store_error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        execution_time = int((time.time() - start_time) * 1000)
        
        # Format result
        result = {
            "reminder_id": reminder_id,
            "task": task,
            "scheduled_time": scheduled_time.isoformat(),
            "scheduled_time_human": scheduled_time.strftime("%A, %B %d at %I:%M %p"),
            "time_expression": time_str,
            "status": "scheduled"
        }
        
        return SkillResult(
            success=True,
            result=result,
            error_message=None,
            execution_time_ms=execution_time
        )
