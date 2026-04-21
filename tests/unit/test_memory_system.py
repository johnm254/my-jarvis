"""Unit tests for the Memory System implementation.

These tests verify the MemorySystem class methods for storing conversations,
semantic search, profile management, and episodic memory logging.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4

from jarvis.config import Configuration
from jarvis.memory import (
    MemorySystem,
    MemorySystemError,
    ConversationExchange,
    PersonalProfile,
    ToolCall,
)


@pytest.fixture
def mock_config():
    """Create a mock Configuration object for testing."""
    config = Mock(spec=Configuration)
    config.supabase_url = "https://test.supabase.co"
    config.supabase_key = "test_key"
    return config


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    client = MagicMock()
    
    # Mock table operations
    client.table.return_value = client
    client.select.return_value = client
    client.insert.return_value = client
    client.update.return_value = client
    client.eq.return_value = client
    client.order.return_value = client
    client.limit.return_value = client
    client.rpc.return_value = client
    
    # Mock execute to return successful result
    mock_result = MagicMock()
    mock_result.data = []
    client.execute.return_value = mock_result
    
    return client


@pytest.fixture
def memory_system(mock_config, mock_supabase_client):
    """Create a MemorySystem instance with mocked dependencies."""
    with patch('jarvis.memory.memory_system.create_client', return_value=mock_supabase_client):
        system = MemorySystem(mock_config)
        system.client = mock_supabase_client
        return system


class TestMemorySystemInitialization:
    """Tests for MemorySystem initialization."""
    
    def test_initialization_success(self, mock_config):
        """Test successful initialization of MemorySystem."""
        with patch('jarvis.memory.memory_system.create_client') as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client
            
            system = MemorySystem(mock_config)
            
            assert system.config == mock_config
            assert system.client == mock_client
            mock_create.assert_called_once()
    
    def test_initialization_failure(self, mock_config):
        """Test MemorySystem initialization failure handling."""
        with patch('jarvis.memory.memory_system.create_client', side_effect=Exception("Connection failed")):
            with pytest.raises(MemorySystemError) as exc_info:
                MemorySystem(mock_config)
            
            assert "Failed to connect to Supabase" in str(exc_info.value)


class TestStoreConversation:
    """Tests for store_conversation method."""
    
    def test_store_conversation_success(self, memory_system, mock_supabase_client):
        """Test successful conversation storage."""
        # Prepare test data
        session_id = "test_session_123"
        exchange = ConversationExchange(
            session_id=session_id,
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            user_input="What's the weather?",
            brain_response="The weather is sunny.",
            tool_calls=[],
            confidence_score=85,
            embedding=[0.1] * 1536
        )
        
        # Mock successful insert
        mock_result = MagicMock()
        mock_result.data = [{"id": str(uuid4())}]
        mock_supabase_client.execute.return_value = mock_result
        
        # Execute
        memory_system.store_conversation(session_id, exchange)
        
        # Verify
        mock_supabase_client.table.assert_called_with("conversations")
        mock_supabase_client.insert.assert_called_once()
        
        # Check the data passed to insert
        call_args = mock_supabase_client.insert.call_args[0][0]
        assert call_args["session_id"] == session_id
        assert call_args["user_input"] == "What's the weather?"
        assert call_args["brain_response"] == "The weather is sunny."
        assert call_args["confidence_score"] == 85
        assert len(call_args["embedding"]) == 1536
    
    def test_store_conversation_failure(self, memory_system, mock_supabase_client):
        """Test conversation storage failure handling."""
        session_id = "test_session_123"
        exchange = ConversationExchange(
            session_id=session_id,
            timestamp=datetime.utcnow(),
            user_input="Test",
            brain_response="Response",
            tool_calls=[],
            confidence_score=80,
            embedding=[0.1] * 1536
        )
        
        # Mock failure
        mock_supabase_client.execute.side_effect = Exception("Database error")
        
        # Execute and verify
        with pytest.raises(MemorySystemError) as exc_info:
            memory_system.store_conversation(session_id, exchange)
        
        assert "Failed to store conversation" in str(exc_info.value)


class TestSemanticSearch:
    """Tests for semantic_search method."""
    
    def test_semantic_search_with_rpc(self, memory_system, mock_supabase_client):
        """Test semantic search using RPC function."""
        query_embedding = [0.2] * 1536
        
        # Mock RPC result
        mock_result = MagicMock()
        mock_result.data = [
            {
                "id": str(uuid4()),
                "user_input": "Previous question",
                "brain_response": "Previous answer",
                "similarity": 0.85
            }
        ]
        mock_supabase_client.execute.return_value = mock_result
        
        # Execute
        results = memory_system.semantic_search(query_embedding, limit=5)
        
        # Verify
        assert len(results) == 1
        assert results[0]["similarity"] == 0.85
        mock_supabase_client.rpc.assert_called_once()
    
    def test_semantic_search_no_results(self, memory_system, mock_supabase_client):
        """Test semantic search with no matching results."""
        query_embedding = [0.2] * 1536
        
        # Mock empty result
        mock_result = MagicMock()
        mock_result.data = None
        mock_supabase_client.execute.return_value = mock_result
        
        # Execute
        results = memory_system.semantic_search(query_embedding)
        
        # Verify
        assert results == []
    
    def test_semantic_search_fallback(self, memory_system, mock_supabase_client):
        """Test semantic search fallback when RPC fails."""
        query_embedding = [0.5] * 1536
        
        # Mock RPC failure, then successful fallback
        mock_supabase_client.rpc.side_effect = Exception("RPC not found")
        
        # Mock fallback query result
        mock_result = MagicMock()
        mock_result.data = [
            {
                "id": str(uuid4()),
                "user_input": "Test",
                "brain_response": "Response",
                "embedding": [0.5] * 1536
            }
        ]
        mock_supabase_client.execute.return_value = mock_result
        
        # Execute
        results = memory_system.semantic_search(query_embedding, limit=5)
        
        # Verify fallback was used
        assert isinstance(results, list)


class TestGetPersonalProfile:
    """Tests for get_personal_profile method."""
    
    def test_get_existing_profile(self, memory_system, mock_supabase_client):
        """Test retrieving an existing user profile."""
        # Mock profile data
        mock_result = MagicMock()
        mock_result.data = [{
            "user_id": "test_user",
            "first_name": "Alice",
            "timezone": "America/Los_Angeles",
            "preferences": {"theme": "dark"},
            "habits": {"morning_routine": "coffee"},
            "interests": ["AI", "coding"],
            "communication_style": "technical",
            "work_hours": {"start": "09:00", "end": "17:00"}
        }]
        mock_supabase_client.execute.return_value = mock_result
        
        # Execute
        profile = memory_system.get_personal_profile("test_user")
        
        # Verify
        assert isinstance(profile, PersonalProfile)
        assert profile.user_id == "test_user"
        assert profile.first_name == "Alice"
        assert profile.timezone == "America/Los_Angeles"
        assert profile.preferences["theme"] == "dark"
        assert "AI" in profile.interests
    
    def test_get_nonexistent_profile_creates_default(self, memory_system, mock_supabase_client):
        """Test that a default profile is created when none exists."""
        # Mock empty result for select, then success for insert
        select_result = MagicMock()
        select_result.data = []
        
        insert_result = MagicMock()
        insert_result.data = [{"user_id": "new_user"}]
        
        mock_supabase_client.execute.side_effect = [select_result, insert_result]
        
        # Execute
        profile = memory_system.get_personal_profile("new_user")
        
        # Verify default profile was created
        assert isinstance(profile, PersonalProfile)
        assert profile.user_id == "new_user"
        assert profile.first_name == "Boss"
        assert profile.timezone == "UTC"
        assert profile.communication_style == "casual"


class TestUpdatePreference:
    """Tests for update_preference method."""
    
    def test_update_preference_success(self, memory_system, mock_supabase_client):
        """Test successful preference update."""
        # Mock get_personal_profile
        with patch.object(memory_system, 'get_personal_profile') as mock_get:
            mock_profile = PersonalProfile(
                user_id="test_user",
                first_name="Bob",
                timezone="UTC",
                preferences={"theme": "light"}
            )
            mock_get.return_value = mock_profile
            
            # Mock update result
            mock_result = MagicMock()
            mock_result.data = [{"user_id": "test_user"}]
            mock_supabase_client.execute.return_value = mock_result
            
            # Execute
            memory_system.update_preference("test_user", "language", "python")
            
            # Verify
            mock_supabase_client.table.assert_called_with("personal_profile")
            mock_supabase_client.update.assert_called_once()
            
            # Check updated preferences
            update_call = mock_supabase_client.update.call_args[0][0]
            assert update_call["preferences"]["language"] == "python"
            assert update_call["preferences"]["theme"] == "light"  # Existing pref preserved
    
    def test_update_preference_failure(self, memory_system, mock_supabase_client):
        """Test preference update failure handling."""
        with patch.object(memory_system, 'get_personal_profile') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            with pytest.raises(MemorySystemError) as exc_info:
                memory_system.update_preference("test_user", "key", "value")
            
            assert "Failed to update preference" in str(exc_info.value)


class TestLogEpisodicMemory:
    """Tests for log_episodic_memory method."""
    
    def test_log_episodic_memory_success(self, memory_system, mock_supabase_client):
        """Test successful episodic memory logging."""
        # Mock successful insert
        mock_result = MagicMock()
        mock_result.data = [{"id": str(uuid4())}]
        mock_supabase_client.execute.return_value = mock_result
        
        # Execute
        memory_system.log_episodic_memory(
            interaction_type="tool_call",
            context="User asked for weather",
            action_taken="Called get_weather skill",
            outcome="Returned weather data",
            success=True
        )
        
        # Verify
        mock_supabase_client.table.assert_called_with("episodic_memory")
        mock_supabase_client.insert.assert_called_once()
        
        # Check the data
        call_args = mock_supabase_client.insert.call_args[0][0]
        assert call_args["interaction_type"] == "tool_call"
        assert call_args["context"] == "User asked for weather"
        assert call_args["success"] is True
    
    def test_log_episodic_memory_failure(self, memory_system, mock_supabase_client):
        """Test episodic memory logging failure handling."""
        mock_supabase_client.execute.side_effect = Exception("Database error")
        
        with pytest.raises(MemorySystemError) as exc_info:
            memory_system.log_episodic_memory(
                interaction_type="conversation",
                context="Test",
                action_taken="Test",
                outcome="Test"
            )
        
        assert "Failed to log episodic memory" in str(exc_info.value)


class TestInjectContext:
    """Tests for inject_context method."""
    
    def test_inject_context_with_profile_only(self, memory_system, mock_supabase_client):
        """Test context injection with user profile only."""
        # Mock profile
        with patch.object(memory_system, 'get_personal_profile') as mock_get:
            mock_profile = PersonalProfile(
                user_id="test_user",
                first_name="Charlie",
                timezone="Europe/London",
                preferences={"theme": "dark"},
                interests=["music", "art"],
                communication_style="casual"
            )
            mock_get.return_value = mock_profile
            
            # Mock empty recent conversations
            mock_result = MagicMock()
            mock_result.data = []
            mock_supabase_client.execute.return_value = mock_result
            
            # Execute
            context = memory_system.inject_context("session_123")
            
            # Verify
            assert "## User Profile" in context
            assert "Charlie" in context
            assert "Europe/London" in context
            assert "casual" in context
            assert "music" in context
    
    def test_inject_context_with_semantic_search(self, memory_system, mock_supabase_client):
        """Test context injection with semantic search."""
        query_embedding = [0.3] * 1536
        
        # Mock profile
        with patch.object(memory_system, 'get_personal_profile') as mock_get:
            mock_profile = PersonalProfile(
                user_id="test_user",
                first_name="Dave",
                timezone="UTC"
            )
            mock_get.return_value = mock_profile
            
            # Mock semantic search
            with patch.object(memory_system, 'semantic_search') as mock_search:
                mock_search.return_value = [
                    {
                        "timestamp": "2024-01-15T10:00:00",
                        "user_input": "Previous question",
                        "brain_response": "Previous answer",
                        "similarity": 0.88
                    }
                ]
                
                # Mock empty recent conversations
                mock_result = MagicMock()
                mock_result.data = []
                mock_supabase_client.execute.return_value = mock_result
                
                # Execute
                context = memory_system.inject_context("session_123", query_embedding)
                
                # Verify
                assert "## Relevant Past Conversations" in context
                assert "Previous question" in context
                assert "Previous answer" in context
                assert "0.88" in context
    
    def test_inject_context_with_recent_history(self, memory_system, mock_supabase_client):
        """Test context injection with recent session history."""
        # Mock profile
        with patch.object(memory_system, 'get_personal_profile') as mock_get:
            mock_profile = PersonalProfile(
                user_id="test_user",
                first_name="Eve",
                timezone="UTC"
            )
            mock_get.return_value = mock_profile
            
            # Mock recent conversations
            mock_result = MagicMock()
            mock_result.data = [
                {
                    "timestamp": "2024-01-15T10:00:00",
                    "user_input": "Hello",
                    "brain_response": "Hi there!"
                },
                {
                    "timestamp": "2024-01-15T10:01:00",
                    "user_input": "How are you?",
                    "brain_response": "I'm doing well!"
                }
            ]
            mock_supabase_client.execute.return_value = mock_result
            
            # Execute
            context = memory_system.inject_context("session_123")
            
            # Verify
            assert "## Recent Session History" in context
            assert "Hello" in context
            assert "Hi there!" in context
    
    def test_inject_context_handles_errors_gracefully(self, memory_system, mock_supabase_client):
        """Test that context injection handles partial failures gracefully."""
        # Mock profile failure
        with patch.object(memory_system, 'get_personal_profile', side_effect=Exception("Profile error")):
            # Mock empty recent conversations
            mock_result = MagicMock()
            mock_result.data = []
            mock_supabase_client.execute.return_value = mock_result
            
            # Execute - should not raise, just log warning
            context = memory_system.inject_context("session_123")
            
            # Verify we get some context even with profile failure
            assert isinstance(context, str)


class TestClose:
    """Tests for close method."""
    
    def test_close_success(self, memory_system):
        """Test successful cleanup."""
        # Should not raise any exceptions
        memory_system.close()
