"""Unit tests for Memory System data models.

Tests the ConversationExchange, PersonalProfile, EpisodicMemory, and ToolCall
dataclasses to ensure they can be instantiated correctly and have the expected
attributes.
"""

from datetime import datetime

import pytest

from jarvis.memory.models import (
    ConversationExchange,
    EpisodicMemory,
    PersonalProfile,
    ToolCall,
)


class TestToolCall:
    """Tests for the ToolCall dataclass."""

    def test_tool_call_creation_success(self):
        """Test creating a successful ToolCall."""
        tool_call = ToolCall(
            tool_name="web_search",
            parameters={"query": "Python tutorials"},
            result={"results": ["result1", "result2"]},
            execution_time_ms=250,
            success=True,
            error_message=None,
        )

        assert tool_call.tool_name == "web_search"
        assert tool_call.parameters == {"query": "Python tutorials"}
        assert tool_call.result == {"results": ["result1", "result2"]}
        assert tool_call.execution_time_ms == 250
        assert tool_call.success is True
        assert tool_call.error_message is None

    def test_tool_call_creation_failure(self):
        """Test creating a failed ToolCall with error message."""
        tool_call = ToolCall(
            tool_name="get_weather",
            parameters={"location": "InvalidCity"},
            result=None,
            execution_time_ms=100,
            success=False,
            error_message="Location not found",
        )

        assert tool_call.tool_name == "get_weather"
        assert tool_call.success is False
        assert tool_call.error_message == "Location not found"

    def test_tool_call_default_error_message(self):
        """Test that error_message defaults to None."""
        tool_call = ToolCall(
            tool_name="system_status",
            parameters={},
            result={"cpu": 45.2},
            execution_time_ms=50,
            success=True,
        )

        assert tool_call.error_message is None


class TestConversationExchange:
    """Tests for the ConversationExchange dataclass."""

    def test_conversation_exchange_creation(self):
        """Test creating a ConversationExchange with all fields."""
        timestamp = datetime.now()
        tool_calls = [
            ToolCall(
                tool_name="web_search",
                parameters={"query": "test"},
                result={"results": []},
                execution_time_ms=200,
                success=True,
            )
        ]
        embedding = [0.1] * 1536  # Typical OpenAI embedding dimension

        exchange = ConversationExchange(
            session_id="session_123",
            timestamp=timestamp,
            user_input="What's the weather?",
            brain_response="Let me check that for you.",
            tool_calls=tool_calls,
            confidence_score=85,
            embedding=embedding,
        )

        assert exchange.session_id == "session_123"
        assert exchange.timestamp == timestamp
        assert exchange.user_input == "What's the weather?"
        assert exchange.brain_response == "Let me check that for you."
        assert len(exchange.tool_calls) == 1
        assert exchange.tool_calls[0].tool_name == "web_search"
        assert exchange.confidence_score == 85
        assert len(exchange.embedding) == 1536

    def test_conversation_exchange_empty_tool_calls(self):
        """Test ConversationExchange with no tool calls."""
        exchange = ConversationExchange(
            session_id="session_456",
            timestamp=datetime.now(),
            user_input="Hello",
            brain_response="Hi there!",
            tool_calls=[],
            confidence_score=95,
            embedding=[0.0] * 1536,
        )

        assert len(exchange.tool_calls) == 0
        assert exchange.confidence_score == 95

    def test_conversation_exchange_low_confidence(self):
        """Test ConversationExchange with low confidence score."""
        exchange = ConversationExchange(
            session_id="session_789",
            timestamp=datetime.now(),
            user_input="Complex question",
            brain_response="I'm not entirely sure, but...",
            tool_calls=[],
            confidence_score=45,
            embedding=[0.0] * 1536,
        )

        assert exchange.confidence_score == 45
        assert exchange.confidence_score < 70  # Below uncertainty threshold


class TestPersonalProfile:
    """Tests for the PersonalProfile dataclass."""

    def test_personal_profile_creation_full(self):
        """Test creating a PersonalProfile with all fields specified."""
        profile = PersonalProfile(
            user_id="user_001",
            first_name="Alice",
            timezone="America/Los_Angeles",
            preferences={"theme": "dark", "voice_enabled": True},
            habits={"morning_routine": "coffee at 7am"},
            interests=["AI", "Python", "Music"],
            communication_style="technical",
            work_hours={"start": "09:00", "end": "17:00"},
        )

        assert profile.user_id == "user_001"
        assert profile.first_name == "Alice"
        assert profile.timezone == "America/Los_Angeles"
        assert profile.preferences["theme"] == "dark"
        assert profile.habits["morning_routine"] == "coffee at 7am"
        assert "AI" in profile.interests
        assert profile.communication_style == "technical"
        assert profile.work_hours["start"] == "09:00"

    def test_personal_profile_defaults(self):
        """Test PersonalProfile with default values."""
        profile = PersonalProfile(
            user_id="user_002",
            first_name="Bob",
            timezone="America/New_York",
        )

        assert profile.preferences == {}
        assert profile.habits == {}
        assert profile.interests == []
        assert profile.communication_style == "casual"
        assert profile.work_hours == {"start": "09:00", "end": "18:00"}

    def test_personal_profile_mutable_defaults(self):
        """Test that default mutable fields are independent across instances."""
        profile1 = PersonalProfile(
            user_id="user_003",
            first_name="Charlie",
            timezone="UTC",
        )
        profile2 = PersonalProfile(
            user_id="user_004",
            first_name="Diana",
            timezone="UTC",
        )

        profile1.preferences["key"] = "value1"
        profile2.preferences["key"] = "value2"

        assert profile1.preferences["key"] == "value1"
        assert profile2.preferences["key"] == "value2"
        assert profile1.preferences is not profile2.preferences

    def test_personal_profile_communication_styles(self):
        """Test different communication styles."""
        technical_profile = PersonalProfile(
            user_id="user_005",
            first_name="Eve",
            timezone="UTC",
            communication_style="technical",
        )
        casual_profile = PersonalProfile(
            user_id="user_006",
            first_name="Frank",
            timezone="UTC",
            communication_style="casual",
        )

        assert technical_profile.communication_style == "technical"
        assert casual_profile.communication_style == "casual"


class TestEpisodicMemory:
    """Tests for the EpisodicMemory dataclass."""

    def test_episodic_memory_creation_success(self):
        """Test creating a successful EpisodicMemory."""
        timestamp = datetime.now()
        memory = EpisodicMemory(
            id="mem_001",
            timestamp=timestamp,
            interaction_type="conversation",
            context="User asked about weather",
            action_taken="Called get_weather skill",
            outcome="Provided weather forecast for Seattle",
            success=True,
        )

        assert memory.id == "mem_001"
        assert memory.timestamp == timestamp
        assert memory.interaction_type == "conversation"
        assert memory.context == "User asked about weather"
        assert memory.action_taken == "Called get_weather skill"
        assert memory.outcome == "Provided weather forecast for Seattle"
        assert memory.success is True

    def test_episodic_memory_creation_failure(self):
        """Test creating a failed EpisodicMemory."""
        memory = EpisodicMemory(
            id="mem_002",
            timestamp=datetime.now(),
            interaction_type="tool_call",
            context="User requested email summary",
            action_taken="Called manage_email skill",
            outcome="Gmail API authentication failed",
            success=False,
        )

        assert memory.interaction_type == "tool_call"
        assert memory.success is False
        assert "failed" in memory.outcome.lower()

    def test_episodic_memory_interaction_types(self):
        """Test different interaction types."""
        conversation_memory = EpisodicMemory(
            id="mem_003",
            timestamp=datetime.now(),
            interaction_type="conversation",
            context="General chat",
            action_taken="Responded to greeting",
            outcome="User greeted",
            success=True,
        )
        hook_memory = EpisodicMemory(
            id="mem_004",
            timestamp=datetime.now(),
            interaction_type="hook",
            context="Morning brief scheduled",
            action_taken="Executed daily_brief hook",
            outcome="Delivered morning summary",
            success=True,
        )

        assert conversation_memory.interaction_type == "conversation"
        assert hook_memory.interaction_type == "hook"


class TestDataModelIntegration:
    """Integration tests for data models working together."""

    def test_conversation_exchange_with_multiple_tool_calls(self):
        """Test ConversationExchange containing multiple ToolCalls."""
        tool_calls = [
            ToolCall(
                tool_name="get_weather",
                parameters={"location": "Seattle"},
                result={"temp": 65, "condition": "Cloudy"},
                execution_time_ms=150,
                success=True,
            ),
            ToolCall(
                tool_name="manage_calendar",
                parameters={"action": "read"},
                result={"events": []},
                execution_time_ms=300,
                success=True,
            ),
        ]

        exchange = ConversationExchange(
            session_id="session_multi",
            timestamp=datetime.now(),
            user_input="What's my day looking like?",
            brain_response="It's cloudy and 65°F. You have no events today.",
            tool_calls=tool_calls,
            confidence_score=90,
            embedding=[0.0] * 1536,
        )

        assert len(exchange.tool_calls) == 2
        assert exchange.tool_calls[0].tool_name == "get_weather"
        assert exchange.tool_calls[1].tool_name == "manage_calendar"
        assert all(tc.success for tc in exchange.tool_calls)

    def test_personal_profile_with_complex_preferences(self):
        """Test PersonalProfile with nested preference structures."""
        profile = PersonalProfile(
            user_id="user_complex",
            first_name="Grace",
            timezone="Europe/London",
            preferences={
                "notifications": {
                    "email": True,
                    "voice": False,
                },
                "skills": {
                    "web_search": {"default_engine": "brave"},
                    "weather": {"units": "celsius"},
                },
            },
            habits={
                "daily_patterns": {
                    "morning": "check email at 8am",
                    "evening": "review calendar at 6pm",
                }
            },
        )

        assert profile.preferences["notifications"]["email"] is True
        assert profile.preferences["skills"]["weather"]["units"] == "celsius"
        assert "morning" in profile.habits["daily_patterns"]
