"""Integration tests for the Memory System with Supabase.

These tests demonstrate how the MemorySystem would work with a real Supabase instance.
They are skipped by default unless SUPABASE_URL and SUPABASE_KEY are set in environment.
"""

import os
import pytest
from datetime import datetime
from uuid import uuid4

from jarvis.config import Configuration
from jarvis.memory import (
    MemorySystem,
    ConversationExchange,
    PersonalProfile,
)


# Skip all tests in this module if Supabase credentials are not available
pytestmark = pytest.mark.skipif(
    not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"),
    reason="Supabase credentials not available. Set SUPABASE_URL and SUPABASE_KEY to run integration tests."
)


@pytest.fixture
def config():
    """Create a Configuration object with real Supabase credentials."""
    return Configuration(
        llm_api_key="test_key",
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_KEY"),
        jwt_secret="test_secret"
    )


@pytest.fixture
def memory_system(config):
    """Create a MemorySystem instance with real Supabase connection."""
    system = MemorySystem(config)
    yield system
    system.close()


class TestMemorySystemIntegration:
    """Integration tests for MemorySystem with real Supabase database."""
    
    def test_store_and_retrieve_conversation(self, memory_system):
        """Test storing a conversation and retrieving it."""
        session_id = f"test_session_{uuid4()}"
        
        # Create a conversation exchange
        exchange = ConversationExchange(
            session_id=session_id,
            timestamp=datetime.utcnow(),
            user_input="What is the capital of France?",
            brain_response="The capital of France is Paris.",
            tool_calls=[],
            confidence_score=95,
            embedding=[0.1] * 1536  # Mock embedding
        )
        
        # Store the conversation
        memory_system.store_conversation(session_id, exchange)
        
        # Verify it was stored by checking recent session history
        context = memory_system.inject_context(session_id)
        assert "What is the capital of France?" in context
        assert "Paris" in context
    
    def test_profile_management(self, memory_system):
        """Test creating and updating user profiles."""
        user_id = f"test_user_{uuid4()}"
        
        # Get profile (should create default if not exists)
        profile = memory_system.get_personal_profile(user_id)
        assert profile.user_id == user_id
        assert profile.first_name == "Boss"
        
        # Update a preference
        memory_system.update_preference(user_id, "favorite_color", "blue")
        
        # Retrieve and verify
        updated_profile = memory_system.get_personal_profile(user_id)
        assert updated_profile.preferences["favorite_color"] == "blue"
    
    def test_episodic_memory_logging(self, memory_system):
        """Test logging episodic memories."""
        # Log an interaction
        memory_system.log_episodic_memory(
            interaction_type="test_interaction",
            context="Integration test context",
            action_taken="Tested episodic memory logging",
            outcome="Successfully logged",
            success=True
        )
        
        # Note: We don't have a direct retrieval method for episodic memories
        # in the current implementation, but this verifies the logging works
        # without raising exceptions
    
    def test_semantic_search(self, memory_system):
        """Test semantic search functionality."""
        # Create a query embedding (in real use, this would come from an embedding model)
        query_embedding = [0.2] * 1536
        
        # Perform semantic search
        results = memory_system.semantic_search(
            query_embedding,
            limit=5,
            similarity_threshold=0.5
        )
        
        # Verify results structure (may be empty if no similar conversations exist)
        assert isinstance(results, list)
        for result in results:
            assert "user_input" in result or "similarity" in result
    
    def test_context_injection(self, memory_system):
        """Test context injection with profile and history."""
        session_id = f"test_session_{uuid4()}"
        user_id = "default_user"
        
        # Store a conversation first
        exchange = ConversationExchange(
            session_id=session_id,
            timestamp=datetime.utcnow(),
            user_input="Test question",
            brain_response="Test answer",
            tool_calls=[],
            confidence_score=80,
            embedding=[0.3] * 1536
        )
        memory_system.store_conversation(session_id, exchange)
        
        # Inject context
        context = memory_system.inject_context(session_id)
        
        # Verify context contains expected sections
        assert "## User Profile" in context
        assert "## Recent Session History" in context or "Test question" in context


if __name__ == "__main__":
    # Allow running integration tests directly if credentials are set
    pytest.main([__file__, "-v"])
