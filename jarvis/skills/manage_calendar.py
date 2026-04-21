"""Calendar Management Skill for JARVIS using Google Calendar API.

Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
"""

import os
import time
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

from jarvis.skills.base import Skill, SkillResult


class ManageCalendarSkill(Skill):
    """
    Calendar management skill that integrates with Google Calendar API.
    
    Supports read, create, and update actions for calendar events.
    Requires confirmation before creating or updating events.
    
    Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
    """
    
    def __init__(self):
        """Initialize the calendar management skill."""
        super().__init__()
        self._name = "manage_calendar"
        self._description = "Manage Google Calendar events. Supports reading events, creating new events, and updating existing events. Requires confirmation before creating or updating."
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform on calendar",
                    "enum": ["read", "create", "update"]
                },
                "details": {
                    "type": "object",
                    "description": "Details for the calendar action. For 'read': optional 'days_ahead' (default 7). For 'create': 'title', 'start_time', 'end_time', optional 'description', 'location'. For 'update': 'event_id', and fields to update.",
                    "properties": {
                        "days_ahead": {
                            "type": "integer",
                            "description": "Number of days ahead to read events (for read action)"
                        },
                        "title": {
                            "type": "string",
                            "description": "Event title (for create/update actions)"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Event start time in ISO format (for create action)"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "Event end time in ISO format (for create action)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Event description (optional, for create/update actions)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Event location (optional, for create/update actions)"
                        },
                        "event_id": {
                            "type": "string",
                            "description": "Event ID to update (for update action)"
                        },
                        "confirmed": {
                            "type": "boolean",
                            "description": "User confirmation for create/update actions (required)"
                        }
                    }
                }
            },
            "required": ["action", "details"]
        }
        
        # Google Calendar credentials path from environment
        self._credentials_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
        
        # Note: In a full implementation, this would use the Google Calendar MCP tool
        # For now, we'll provide a mock implementation that demonstrates the interface
        self._mcp_available = False
    
    def _check_credentials(self) -> tuple[bool, Optional[str]]:
        """
        Check if Google Calendar credentials are configured.
        
        Returns:
            Tuple of (is_configured, error_message)
        """
        if not self._credentials_path:
            return False, "Google Calendar credentials not configured. Please set GOOGLE_CALENDAR_CREDENTIALS in .env file."
        
        # In full implementation, would validate credentials file exists and is valid
        return True, None
    
    def _read_events(self, details: Dict[str, Any]) -> tuple[bool, Any, Optional[str]]:
        """
        Read calendar events.
        
        Args:
            details: Dictionary with optional 'days_ahead' parameter
            
        Returns:
            Tuple of (success, result, error_message)
        """
        days_ahead = details.get("days_ahead", 7)
        
        # In full implementation, this would use Google Calendar MCP tool
        # For now, return a mock response indicating MCP integration needed
        if not self._mcp_available:
            return (
                False,
                None,
                "Google Calendar MCP tool not yet integrated. This skill requires MCP tool setup."
            )
        
        # Mock implementation structure:
        # 1. Use MCP tool to call Google Calendar API
        # 2. Get events from now to now + days_ahead
        # 3. Format and return events
        
        return True, {"events": [], "days_ahead": days_ahead}, None
    
    def _create_event(self, details: Dict[str, Any]) -> tuple[bool, Any, Optional[str]]:
        """
        Create a new calendar event.
        
        Args:
            details: Dictionary with event details (title, start_time, end_time, etc.)
            
        Returns:
            Tuple of (success, result, error_message)
        """
        # Validate required fields for create action
        required_fields = ["title", "start_time", "end_time"]
        missing_fields = [field for field in required_fields if field not in details]
        
        if missing_fields:
            return (
                False,
                None,
                f"Missing required fields for create action: {', '.join(missing_fields)}"
            )
        
        # Check for user confirmation (requirement 7.7)
        if not details.get("confirmed", False):
            return (
                False,
                None,
                "User confirmation required before creating calendar event. Please confirm the event details."
            )
        
        # Validate time format
        try:
            start_time = datetime.fromisoformat(details["start_time"].replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(details["end_time"].replace("Z", "+00:00"))
            
            if end_time <= start_time:
                return (
                    False,
                    None,
                    "Event end time must be after start time"
                )
        except (ValueError, AttributeError) as e:
            return (
                False,
                None,
                f"Invalid time format. Use ISO format (e.g., '2024-01-15T10:00:00'): {str(e)}"
            )
        
        # In full implementation, this would use Google Calendar MCP tool
        if not self._mcp_available:
            return (
                False,
                None,
                "Google Calendar MCP tool not yet integrated. This skill requires MCP tool setup."
            )
        
        # Mock implementation structure:
        # 1. Use MCP tool to call Google Calendar API
        # 2. Create event with provided details
        # 3. Return created event details
        
        return True, {"event_id": "mock_event_id", "status": "created"}, None
    
    def _update_event(self, details: Dict[str, Any]) -> tuple[bool, Any, Optional[str]]:
        """
        Update an existing calendar event.
        
        Args:
            details: Dictionary with event_id and fields to update
            
        Returns:
            Tuple of (success, result, error_message)
        """
        # Validate event_id is provided
        if "event_id" not in details:
            return (
                False,
                None,
                "Missing required field for update action: event_id"
            )
        
        # Check for user confirmation (requirement 7.7)
        if not details.get("confirmed", False):
            return (
                False,
                None,
                "User confirmation required before updating calendar event. Please confirm the changes."
            )
        
        # Validate time format if times are being updated
        if "start_time" in details or "end_time" in details:
            try:
                if "start_time" in details:
                    datetime.fromisoformat(details["start_time"].replace("Z", "+00:00"))
                if "end_time" in details:
                    datetime.fromisoformat(details["end_time"].replace("Z", "+00:00"))
            except (ValueError, AttributeError) as e:
                return (
                    False,
                    None,
                    f"Invalid time format. Use ISO format (e.g., '2024-01-15T10:00:00'): {str(e)}"
                )
        
        # In full implementation, this would use Google Calendar MCP tool
        if not self._mcp_available:
            return (
                False,
                None,
                "Google Calendar MCP tool not yet integrated. This skill requires MCP tool setup."
            )
        
        # Mock implementation structure:
        # 1. Use MCP tool to call Google Calendar API
        # 2. Update event with provided details
        # 3. Return updated event details
        
        return True, {"event_id": details["event_id"], "status": "updated"}, None
    
    def execute(self, **kwargs) -> SkillResult:
        """
        Execute calendar management action.
        
        Args:
            **kwargs: Must contain 'action' and 'details' parameters
            
        Returns:
            SkillResult with calendar operation result
            
        Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
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
        
        action = kwargs.get("action")
        details = kwargs.get("details", {})
        
        # Check credentials
        creds_ok, creds_error = self._check_credentials()
        if not creds_ok:
            return SkillResult(
                success=False,
                result=None,
                error_message=creds_error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Execute action based on type (requirements 7.2, 7.3, 7.4, 7.5)
        if action == "read":
            success, result, error = self._read_events(details)
        elif action == "create":
            success, result, error = self._create_event(details)
        elif action == "update":
            success, result, error = self._update_event(details)
        else:
            return SkillResult(
                success=False,
                result=None,
                error_message=f"Unsupported action: {action}. Supported actions: read, create, update",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        execution_time = int((time.time() - start_time) * 1000)
        
        if not success:
            return SkillResult(
                success=False,
                result=result,
                error_message=error,
                execution_time_ms=execution_time
            )
        
        return SkillResult(
            success=True,
            result=result,
            error_message=None,
            execution_time_ms=execution_time
        )
