"""Email Management Skill for JARVIS using Gmail API.

Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7
"""

import os
import time
from typing import Any, Dict, Optional, List

from jarvis.skills.base import Skill, SkillResult


class ManageEmailSkill(Skill):
    """
    Email management skill that integrates with Gmail API.
    
    Supports read, summarize, and draft actions for email messages.
    Requires explicit confirmation before sending emails.
    
    Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7
    """
    
    def __init__(self):
        """Initialize the email management skill."""
        super().__init__()
        self._name = "manage_email"
        self._description = "Manage Gmail messages. Supports reading messages, generating summaries of unread emails, and drafting messages. Requires explicit confirmation before sending."
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform on email",
                    "enum": ["read", "summarize", "draft"]
                },
                "filters": {
                    "type": "object",
                    "description": "Filters for the email action. For 'read': optional 'max_results' (default 10), 'label' (e.g., 'INBOX', 'UNREAD'). For 'summarize': optional 'label' (default 'UNREAD'). For 'draft': 'to', 'subject', 'body', optional 'confirmed' for sending.",
                    "properties": {
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of messages to retrieve (for read action)"
                        },
                        "label": {
                            "type": "string",
                            "description": "Gmail label to filter by (e.g., 'INBOX', 'UNREAD', 'SENT')"
                        },
                        "to": {
                            "type": "string",
                            "description": "Recipient email address (for draft action)"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject (for draft action)"
                        },
                        "body": {
                            "type": "string",
                            "description": "Email body content (for draft action)"
                        },
                        "confirmed": {
                            "type": "boolean",
                            "description": "User confirmation for sending email (required for draft action)"
                        }
                    }
                }
            },
            "required": ["action", "filters"]
        }
        
        # Gmail credentials path from environment
        self._credentials_path = os.getenv("GMAIL_CREDENTIALS")
        
        # Note: In a full implementation, this would use the Gmail MCP tool
        # For now, we'll provide a mock implementation that demonstrates the interface
        self._mcp_available = False
    
    def _check_credentials(self) -> tuple[bool, Optional[str]]:
        """
        Check if Gmail credentials are configured.
        
        Returns:
            Tuple of (is_configured, error_message)
        """
        if not self._credentials_path:
            return False, "Gmail credentials not configured. Please set GMAIL_CREDENTIALS in .env file."
        
        # In full implementation, would validate credentials file exists and is valid
        return True, None
    
    def _read_messages(self, filters: Dict[str, Any]) -> tuple[bool, Any, Optional[str]]:
        """
        Read email messages from Gmail.
        
        Args:
            filters: Dictionary with optional 'max_results' and 'label' parameters
            
        Returns:
            Tuple of (success, result, error_message)
        """
        max_results = filters.get("max_results", 10)
        label = filters.get("label", "INBOX")
        
        # Validate max_results
        if max_results < 1 or max_results > 100:
            return (
                False,
                None,
                "max_results must be between 1 and 100"
            )
        
        # In full implementation, this would use Gmail MCP tool
        if not self._mcp_available:
            return (
                False,
                None,
                "Gmail MCP tool not yet integrated. This skill requires MCP tool setup."
            )
        
        # Mock implementation structure:
        # 1. Use MCP tool to call Gmail API
        # 2. Get messages with specified label and max_results
        # 3. Format and return messages
        
        return True, {
            "messages": [],
            "count": 0,
            "label": label,
            "max_results": max_results
        }, None
    
    def _summarize_messages(self, filters: Dict[str, Any]) -> tuple[bool, Any, Optional[str]]:
        """
        Generate a summary of unread email messages.
        
        Args:
            filters: Dictionary with optional 'label' parameter (default 'UNREAD')
            
        Returns:
            Tuple of (success, result, error_message)
        """
        label = filters.get("label", "UNREAD")
        
        # In full implementation, this would use Gmail MCP tool
        if not self._mcp_available:
            return (
                False,
                None,
                "Gmail MCP tool not yet integrated. This skill requires MCP tool setup."
            )
        
        # Mock implementation structure:
        # 1. Use MCP tool to call Gmail API
        # 2. Get unread messages
        # 3. Extract key information (sender, subject, snippet)
        # 4. Generate Brain summary of unread emails
        # 5. Return summary
        
        return True, {
            "summary": "No unread messages (mock implementation)",
            "unread_count": 0,
            "label": label
        }, None
    
    def _draft_message(self, filters: Dict[str, Any]) -> tuple[bool, Any, Optional[str]]:
        """
        Create a draft email message.
        
        Args:
            filters: Dictionary with 'to', 'subject', 'body', and optional 'confirmed'
            
        Returns:
            Tuple of (success, result, error_message)
        """
        # Validate required fields for draft action
        required_fields = ["to", "subject", "body"]
        missing_fields = [field for field in required_fields if field not in filters]
        
        if missing_fields:
            return (
                False,
                None,
                f"Missing required fields for draft action: {', '.join(missing_fields)}"
            )
        
        to = filters.get("to")
        subject = filters.get("subject")
        body = filters.get("body")
        confirmed = filters.get("confirmed", False)
        
        # Validate email address format (basic validation)
        if "@" not in to or "." not in to:
            return (
                False,
                None,
                f"Invalid email address format: {to}"
            )
        
        # Check for user confirmation before sending (requirement 8.7)
        if confirmed:
            # User wants to send the email
            if not self._mcp_available:
                return (
                    False,
                    None,
                    "Gmail MCP tool not yet integrated. This skill requires MCP tool setup."
                )
            
            # Mock implementation structure for sending:
            # 1. Use MCP tool to call Gmail API
            # 2. Create and send message
            # 3. Return sent message details
            
            return True, {
                "status": "sent",
                "to": to,
                "subject": subject,
                "message_id": "mock_message_id"
            }, None
        else:
            # User has not confirmed - create draft only
            if not self._mcp_available:
                return (
                    False,
                    None,
                    "Gmail MCP tool not yet integrated. This skill requires MCP tool setup."
                )
            
            # Mock implementation structure for draft:
            # 1. Use MCP tool to call Gmail API
            # 2. Create draft message
            # 3. Return draft details with confirmation prompt
            
            return True, {
                "status": "draft_created",
                "to": to,
                "subject": subject,
                "draft_id": "mock_draft_id",
                "confirmation_required": "Set 'confirmed': true to send this email"
            }, None
    
    def execute(self, **kwargs) -> SkillResult:
        """
        Execute email management action.
        
        Args:
            **kwargs: Must contain 'action' and 'filters' parameters
            
        Returns:
            SkillResult with email operation result
            
        Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7
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
        filters = kwargs.get("filters", {})
        
        # Check credentials
        creds_ok, creds_error = self._check_credentials()
        if not creds_ok:
            return SkillResult(
                success=False,
                result=None,
                error_message=creds_error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Execute action based on type (requirements 8.2, 8.3, 8.4, 8.5)
        if action == "read":
            success, result, error = self._read_messages(filters)
        elif action == "summarize":
            success, result, error = self._summarize_messages(filters)
        elif action == "draft":
            success, result, error = self._draft_message(filters)
        else:
            return SkillResult(
                success=False,
                result=None,
                error_message=f"Unsupported action: {action}. Supported actions: read, summarize, draft",
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
