"""Performance tests for Memory System.

These tests verify that the Memory System meets the performance requirements:
- Semantic search: < 500ms
- Context injection: < 200ms
- Profile updates: < 100ms
"""

import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from jarvis.config import Configuration
from jarvis.memory.memory_system import MemorySystem, MemorySystemError
from jarvis.memory.models import ConversationExchange, PersonalProfile


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = MagicMock(spec=Configuration)
    config.supabase_url = "https://test.supabase.co"
    config.supabase_key = "test_key"
    return config


@pytest.fixture
def memory_system(mock_config):
    """Create a MemorySystem instance with mocked Supabase client."""
    with patch('jarvis.memory.memory_system.create_client') as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        
        system = MemorySystem(mock_config)
        system.client = mock_client
        
        yield system


class TestSemanticSearchPerformance:
    """Performance tests for semantic_search method."""
    
    def test_semantic_search_performance_with_rpc(self, memory_system):
        """Test that semantic search completes within 500ms using RPC."""
        # Mock RPC response with realistic data
        mock_result = MagicMock()
        mock_result.data = [
            {
                "id": "1",
                "user_input": "What's the weather?",
                "brain_response": "It's sunny today.",
                "similarity": 0.92,
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "2",
                "user_input": "Tell me about the weather",
                "brain_response": "The weather is nice.",
                "similarity": 0.88,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        memory_system.client.rpc.return_value.execute.return_value = mock_result
        
        # Measure performance
        query_embedding = [0.1] * 1536
        start_time = time.time()
        
        results = memory_system.semantic_search(query_embedding, limit=5)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Verify performance requirement
        assert elapsed_ms < 500, f"Semantic search took {elapsed_ms:.2f}ms, exceeds 500ms target"
        assert len(results) == 2
        assert results[0]["similarity"] == 0.92
    
    def test_semantic_search_performance_fallback(self, memory_system):
        """Test that semantic search fallback completes within reasonable time."""
        # Mock RPC failure and fallback to manual search
        memory_system.client.rpc.side_effect = Exception("RPC not available")
        
        # Mock table select for fallback
        mock_result = MagicMock()
        mock_result.data = [
            {
                "id": str(i),
                "user_input": f"Query {i}",
                "brain_response": f"Response {i}",
                "embedding": [0.1 + i * 0.01] * 1536,
                "timestamp": datetime.now().isoformat()
            }
            for i in range(10)  # Reduced dataset for fallback
        ]
        
        memory_system.client.table.return_value.select.return_value.limit.return_value.execute.return_value = mock_result
        
        # Measure performance
        query_embedding = [0.15] * 1536
        start_time = time.time()
        
        results = memory_system.semantic_search(query_embedding, limit=5)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Fallback should still be reasonably fast (allow more time than RPC)
        assert elapsed_ms < 1000, f"Fallback semantic search took {elapsed_ms:.2f}ms, too slow"
        assert len(results) <= 5


class TestProfilePerformance:
    """Performance tests for profile operations."""
    
    def test_get_profile_performance_from_database(self, memory_system):
        """Test that getting a profile from database completes quickly."""
        # Mock database response
        mock_result = MagicMock()
        mock_result.data = [{
            "user_id": "test_user",
            "first_name": "Alice",
            "timezone": "America/New_York",
            "preferences": {"theme": "dark"},
            "habits": {},
            "interests": ["AI", "coding"],
            "communication_style": "technical",
            "work_hours": {"start": "09:00", "end": "17:00"}
        }]
        
        memory_system.client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result
        
        # Measure performance
        start_time = time.time()
        
        profile = memory_system.get_personal_profile("test_user")
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Should be very fast (database query + object creation)
        assert elapsed_ms < 100, f"Profile retrieval took {elapsed_ms:.2f}ms, exceeds reasonable time"
        assert profile.first_name == "Alice"
    
    def test_get_profile_performance_from_cache(self, memory_system):
        """Test that getting a cached profile is extremely fast."""
        # Mock database response for first call
        mock_result = MagicMock()
        mock_result.data = [{
            "user_id": "test_user",
            "first_name": "Bob",
            "timezone": "UTC",
            "preferences": {},
            "habits": {},
            "interests": [],
            "communication_style": "casual",
            "work_hours": {"start": "09:00", "end": "18:00"}
        }]
        
        memory_system.client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result
        
        # First call - populates cache
        profile1 = memory_system.get_personal_profile("test_user")
        
        # Second call - should use cache
        start_time = time.time()
        profile2 = memory_system.get_personal_profile("test_user")
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Cached retrieval should be extremely fast (< 1ms typically)
        assert elapsed_ms < 10, f"Cached profile retrieval took {elapsed_ms:.2f}ms, cache not working"
        assert profile1.first_name == profile2.first_name
    
    def test_update_preference_performance(self, memory_system):
        """Test that updating a preference completes within 100ms."""
        # Mock get_personal_profile
        mock_profile_result = MagicMock()
        mock_profile_result.data = [{
            "user_id": "test_user",
            "first_name": "Charlie",
            "timezone": "UTC",
            "preferences": {"theme": "light"},
            "habits": {},
            "interests": [],
            "communication_style": "casual",
            "work_hours": {"start": "09:00", "end": "18:00"}
        }]
        
        memory_system.client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_profile_result
        
        # Mock update
        mock_update_result = MagicMock()
        mock_update_result.data = [{"user_id": "test_user"}]
        memory_system.client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update_result
        
        # Measure performance
        start_time = time.time()
        
        memory_system.update_preference("test_user", "language", "python")
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Verify performance requirement
        assert elapsed_ms < 100, f"Profile update took {elapsed_ms:.2f}ms, exceeds 100ms target"


class TestContextInjectionPerformance:
    """Performance tests for inject_context method."""
    
    def test_inject_context_performance_without_embedding(self, memory_system):
        """Test that context injection without semantic search completes within 200ms."""
        # Mock profile
        mock_profile_result = MagicMock()
        mock_profile_result.data = [{
            "user_id": "default_user",
            "first_name": "Boss",
            "timezone": "UTC",
            "preferences": {"theme": "dark"},
            "habits": {},
            "interests": ["AI"],
            "communication_style": "casual",
            "work_hours": {"start": "09:00", "end": "18:00"}
        }]
        
        memory_system.client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_profile_result
        
        # Mock recent conversations
        mock_conversations_result = MagicMock()
        mock_conversations_result.data = [
            {
                "timestamp": datetime.now().isoformat(),
                "user_input": "Hello",
                "brain_response": "Hi there!"
            }
        ]
        
        memory_system.client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_conversations_result
        
        # Measure performance
        start_time = time.time()
        
        context = memory_system.inject_context("session_123")
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Verify performance requirement
        assert elapsed_ms < 200, f"Context injection took {elapsed_ms:.2f}ms, exceeds 200ms target"
        assert "Boss" in context
        assert "User Profile" in context
    
    def test_inject_context_performance_with_embedding(self, memory_system):
        """Test that context injection with semantic search completes within 200ms."""
        # Mock profile (will use cache after first call)
        mock_profile_result = MagicMock()
        mock_profile_result.data = [{
            "user_id": "default_user",
            "first_name": "Boss",
            "timezone": "UTC",
            "preferences": {},
            "habits": {},
            "interests": [],
            "communication_style": "casual",
            "work_hours": {"start": "09:00", "end": "18:00"}
        }]
        
        memory_system.client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_profile_result
        
        # Mock semantic search RPC
        mock_search_result = MagicMock()
        mock_search_result.data = [
            {
                "user_input": "Previous question",
                "brain_response": "Previous answer",
                "similarity": 0.85,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        memory_system.client.rpc.return_value.execute.return_value = mock_search_result
        
        # Mock recent conversations
        mock_conversations_result = MagicMock()
        mock_conversations_result.data = []
        
        memory_system.client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_conversations_result
        
        # Measure performance
        query_embedding = [0.2] * 1536
        start_time = time.time()
        
        context = memory_system.inject_context("session_123", query_embedding=query_embedding)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Verify performance requirement (may be close to limit with semantic search)
        assert elapsed_ms < 200, f"Context injection with embedding took {elapsed_ms:.2f}ms, exceeds 200ms target"
        assert "Boss" in context


class TestCacheManagement:
    """Tests for cache management functionality."""
    
    def test_cache_invalidation_on_update(self, memory_system):
        """Test that cache is invalidated when profile is updated."""
        # Mock profile
        mock_profile_result = MagicMock()
        mock_profile_result.data = [{
            "user_id": "test_user",
            "first_name": "Dave",
            "timezone": "UTC",
            "preferences": {"theme": "light"},
            "habits": {},
            "interests": [],
            "communication_style": "casual",
            "work_hours": {"start": "09:00", "end": "18:00"}
        }]
        
        memory_system.client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_profile_result
        
        # First call - populates cache
        profile1 = memory_system.get_personal_profile("test_user")
        assert "test_user" in memory_system._profile_cache
        
        # Mock update
        mock_update_result = MagicMock()
        mock_update_result.data = [{"user_id": "test_user"}]
        memory_system.client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update_result
        
        # Update preference - should invalidate cache
        memory_system.update_preference("test_user", "theme", "dark")
        
        # Cache should be cleared
        assert "test_user" not in memory_system._profile_cache
    
    def test_clear_profile_cache_specific_user(self, memory_system):
        """Test clearing cache for a specific user."""
        # Manually add to cache
        from jarvis.memory.models import PersonalProfile
        profile = PersonalProfile(
            user_id="user1",
            first_name="Test",
            timezone="UTC",
            preferences={},
            habits={},
            interests=[],
            communication_style="casual",
            work_hours={"start": "09:00", "end": "18:00"}
        )
        memory_system._profile_cache["user1"] = (profile, time.time())
        memory_system._profile_cache["user2"] = (profile, time.time())
        
        # Clear specific user
        memory_system.clear_profile_cache("user1")
        
        assert "user1" not in memory_system._profile_cache
        assert "user2" in memory_system._profile_cache
    
    def test_clear_all_profile_caches(self, memory_system):
        """Test clearing all profile caches."""
        # Manually add to cache
        from jarvis.memory.models import PersonalProfile
        profile = PersonalProfile(
            user_id="user1",
            first_name="Test",
            timezone="UTC",
            preferences={},
            habits={},
            interests=[],
            communication_style="casual",
            work_hours={"start": "09:00", "end": "18:00"}
        )
        memory_system._profile_cache["user1"] = (profile, time.time())
        memory_system._profile_cache["user2"] = (profile, time.time())
        
        # Clear all
        memory_system.clear_profile_cache()
        
        assert len(memory_system._profile_cache) == 0
