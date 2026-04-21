"""Audit logging for JARVIS system actions.

This module provides centralized audit logging functionality to track all
actions taken by the system on behalf of the user. Logs are stored in the
audit_log database table with timestamps, action types, and outcomes.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from jarvis.config import Configuration
from jarvis.memory.memory_system import MemorySystem

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Centralized audit logging for JARVIS system actions.
    
    Logs all actions to the audit_log table with:
    - Timestamps
    - Action types
    - User IDs
    - Action details
    - Success status
    
    Validates: Requirements 18.5, 18.6
    """
    
    def __init__(self, memory_system: MemorySystem):
        """
        Initialize the audit logger.
        
        Args:
            memory_system: MemorySystem instance for database access
        """
        self.memory_system = memory_system
    
    def log_action(
        self,
        action_type: str,
        user_id: str,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True
    ) -> None:
        """
        Log an action to the audit log.
        
        Args:
            action_type: Type of action (e.g., "conversation", "skill_execution", "settings_update")
            user_id: User who initiated the action
            details: Additional details about the action (stored as JSONB)
            success: Whether the action was successful
        """
        try:
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "action_type": action_type,
                "user_id": user_id,
                "details": details or {},
                "success": success
            }
            
            result = self.memory_system.client.table("audit_log").insert(audit_entry).execute()
            
            if not result.data:
                logger.warning(f"Failed to log audit entry: no data returned")
            
        except Exception as e:
            # Don't fail the operation if audit logging fails
            logger.error(f"Error logging audit entry: {e}")
    
    def log_conversation(
        self,
        user_id: str,
        session_id: str,
        user_input: str,
        brain_response: str,
        confidence_score: int,
        success: bool = True
    ) -> None:
        """
        Log a conversation interaction.
        
        Args:
            user_id: User ID
            session_id: Conversation session ID
            user_input: User's input message
            brain_response: Brain's response
            confidence_score: Confidence score of the response
            success: Whether the conversation was successful
        """
        self.log_action(
            action_type="conversation",
            user_id=user_id,
            details={
                "session_id": session_id,
                "user_input": user_input[:100],  # Truncate for storage
                "response_length": len(brain_response),
                "confidence_score": confidence_score
            },
            success=success
        )
    
    def log_skill_execution(
        self,
        user_id: str,
        skill_name: str,
        parameters: Dict[str, Any],
        execution_time_ms: int,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> None:
        """
        Log a skill execution.
        
        Args:
            user_id: User ID
            skill_name: Name of the skill executed
            parameters: Parameters passed to the skill
            execution_time_ms: Execution time in milliseconds
            success: Whether the skill execution was successful
            error_message: Error message if execution failed
        """
        self.log_action(
            action_type="skill_execution",
            user_id=user_id,
            details={
                "skill_name": skill_name,
                "parameters": parameters,
                "execution_time_ms": execution_time_ms,
                "error_message": error_message
            },
            success=success
        )
    
    def log_settings_update(
        self,
        user_id: str,
        updated_fields: list,
        success: bool = True
    ) -> None:
        """
        Log a settings update.
        
        Args:
            user_id: User ID
            updated_fields: List of fields that were updated
            success: Whether the update was successful
        """
        self.log_action(
            action_type="settings_update",
            user_id=user_id,
            details={
                "updated_fields": updated_fields
            },
            success=success
        )
    
    def log_memory_operation(
        self,
        user_id: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True
    ) -> None:
        """
        Log a memory operation (search, update, delete).
        
        Args:
            user_id: User ID
            operation: Type of operation (search, update, delete)
            details: Additional details about the operation
            success: Whether the operation was successful
        """
        self.log_action(
            action_type=f"memory_{operation}",
            user_id=user_id,
            details=details or {},
            success=success
        )
    
    def log_authentication(
        self,
        user_id: str,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an authentication attempt.
        
        Args:
            user_id: User ID attempting authentication
            success: Whether authentication was successful
            details: Additional details (e.g., IP address, user agent)
        """
        self.log_action(
            action_type="authentication",
            user_id=user_id,
            details=details or {},
            success=success
        )
    
    def log_hook_execution(
        self,
        user_id: str,
        hook_name: str,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> None:
        """
        Log a hook execution.
        
        Args:
            user_id: User ID
            hook_name: Name of the hook executed
            success: Whether the hook execution was successful
            error_message: Error message if execution failed
        """
        self.log_action(
            action_type="hook_execution",
            user_id=user_id,
            details={
                "hook_name": hook_name,
                "error_message": error_message
            },
            success=success
        )


# Global audit logger instance (initialized lazily)
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger(memory_system: MemorySystem) -> AuditLogger:
    """
    Get or create the global audit logger instance.
    
    Args:
        memory_system: MemorySystem instance for database access
        
    Returns:
        AuditLogger instance
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(memory_system)
    return _audit_logger
