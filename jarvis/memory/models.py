"""Data models for the Memory System.

This module defines the core data structures used by the Memory System
for storing conversations, user profiles, episodic memories, and tool calls.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ToolCall:
    """Represents a single tool/skill invocation with execution details.
    
    Attributes:
        tool_name: Name of the skill/tool that was invoked
        parameters: Dictionary of parameters passed to the tool
        result: The result returned by the tool execution
        execution_time_ms: Time taken to execute the tool in milliseconds
        success: Whether the tool execution succeeded
        error_message: Error message if execution failed, None otherwise
    """
    tool_name: str
    parameters: Dict[str, Any]
    result: Any
    execution_time_ms: int
    success: bool
    error_message: Optional[str] = None


@dataclass
class ConversationExchange:
    """Represents a single turn in a conversation between user and JARVIS.
    
    This dataclass stores both the conversational content and metadata needed
    for semantic search and context injection.
    
    Attributes:
        session_id: Unique identifier for the conversation session
        timestamp: When this exchange occurred
        user_input: The user's input text
        brain_response: JARVIS's response text
        tool_calls: List of tools invoked during this exchange
        confidence_score: Brain's confidence in the response (0-100)
        embedding: Vector embedding for semantic search (1536 dimensions for OpenAI)
    """
    session_id: str
    timestamp: datetime
    user_input: str
    brain_response: str
    tool_calls: List[ToolCall]
    confidence_score: int
    embedding: List[float]


@dataclass
class PersonalProfile:
    """Represents a user's personal profile with preferences and learned behaviors.
    
    This dataclass stores all user-specific information that JARVIS learns over time,
    enabling personalized interactions and proactive suggestions.
    
    Attributes:
        user_id: Unique identifier for the user
        first_name: User's first name (used for personalized greetings)
        timezone: User's timezone (e.g., "America/Los_Angeles")
        preferences: Flexible key-value store for user preferences
        habits: Learned patterns and behaviors (e.g., {"morning_routine": "coffee at 7am"})
        interests: List of user interests and topics
        communication_style: Preferred communication style ("technical" or "casual")
        work_hours: Dictionary with work schedule (e.g., {"start": "09:00", "end": "18:00"})
    """
    user_id: str
    first_name: str
    timezone: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    habits: Dict[str, Any] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    communication_style: str = "casual"
    work_hours: Dict[str, str] = field(default_factory=lambda: {"start": "09:00", "end": "18:00"})


@dataclass
class EpisodicMemory:
    """Represents a logged interaction with timestamp and outcome.
    
    Episodic memories provide a time-stamped log of all interactions, enabling
    JARVIS to learn from past experiences and improve over time.
    
    Attributes:
        id: Unique identifier for this memory
        timestamp: When this interaction occurred
        interaction_type: Type of interaction ("conversation", "tool_call", "hook")
        context: Contextual information about the interaction
        action_taken: Description of the action that was performed
        outcome: Description of the result or outcome
        success: Whether the interaction was successful
    """
    id: str
    timestamp: datetime
    interaction_type: str
    context: str
    action_taken: str
    outcome: str
    success: bool
