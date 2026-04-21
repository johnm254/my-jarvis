"""Memory System implementation with Supabase integration.

This module provides the MemorySystem class that handles persistent storage
of conversations, user profiles, episodic memories, and semantic search using
Supabase PostgreSQL with pgvector extension.

Performance optimizations:
- Connection pooling for database operations
- In-memory caching for frequently accessed data (user profiles)
- Optimized query patterns for sub-200ms context injection
- Batch operations where applicable
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions

from jarvis.config import Configuration
from jarvis.memory.models import (
    ConversationExchange,
    EpisodicMemory,
    PersonalProfile,
    ToolCall,
)
from jarvis.metrics import get_metrics_tracker

logger = logging.getLogger(__name__)


class MemorySystemError(Exception):
    """Base exception for Memory System errors."""
    pass


class MemorySystem:
    """Persistent storage system with vector and relational database capabilities.
    
    The MemorySystem provides methods for storing conversations with vector embeddings,
    semantic search, user profile management, and episodic memory logging. It uses
    Supabase (PostgreSQL + pgvector) for storage with connection pooling and
    comprehensive error handling.
    
    Performance optimizations:
    - Connection pooling with optimized timeout settings
    - In-memory profile cache with TTL
    - Performance monitoring for all operations
    - Optimized query patterns for sub-200ms operations
    
    Attributes:
        client: Supabase client instance for database operations
        config: Configuration object with connection details
        _profile_cache: In-memory cache for user profiles
        _profile_cache_ttl: Time-to-live for cached profiles (seconds)
    """
    
    def __init__(self, config: Configuration):
        """Initialize the Memory System with Supabase connection.
        
        Args:
            config: Configuration object containing supabase_url and supabase_key
            
        Raises:
            MemorySystemError: If connection to Supabase fails
        """
        self.config = config
        self.metrics_tracker = get_metrics_tracker()
        
        # Initialize profile cache for performance optimization
        self._profile_cache: Dict[str, tuple[PersonalProfile, float]] = {}
        self._profile_cache_ttl: float = 300.0  # 5 minutes cache TTL
        
        try:
            # Create Supabase client with optimized connection pooling
            # Reduced timeouts for faster failure detection and retry
            options = ClientOptions(
                postgrest_client_timeout=5,  # Reduced from 10s for faster operations
                storage_client_timeout=5,
            )
            self.client: Client = create_client(
                config.supabase_url,
                config.supabase_key,
                options=options
            )
            logger.info("Memory System initialized successfully with connection pooling")
        except Exception as e:
            logger.error(f"Failed to initialize Memory System: {e}")
            raise MemorySystemError(f"Failed to connect to Supabase: {e}")
    
    def store_conversation(
        self,
        session_id: str,
        exchange: ConversationExchange
    ) -> None:
        """Store a conversation turn in vector and relational storage.
        
        This method inserts a conversation exchange into the conversations table
        with its vector embedding for semantic search. The embedding should be
        pre-computed before calling this method.
        
        Args:
            session_id: Unique identifier for the conversation session
            exchange: ConversationExchange object containing the conversation data
            
        Raises:
            MemorySystemError: If database insertion fails
        """
        try:
            # Prepare conversation data for insertion
            conversation_data = {
                "session_id": session_id,
                "timestamp": exchange.timestamp.isoformat(),
                "user_input": exchange.user_input,
                "brain_response": exchange.brain_response,
                "confidence_score": exchange.confidence_score,
                "embedding": exchange.embedding,
            }
            
            # Insert into conversations table
            result = self.client.table("conversations").insert(conversation_data).execute()
            
            if not result.data:
                raise MemorySystemError("Failed to store conversation: no data returned")
            
            logger.debug(f"Stored conversation for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
            raise MemorySystemError(f"Failed to store conversation: {e}")
    
    def semantic_search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search memories by semantic similarity using vector embeddings.
        
        This method performs a cosine similarity search on stored conversation
        embeddings to find the most relevant past conversations.
        
        Performance target: < 500ms
        
        Args:
            query_embedding: Vector embedding of the search query (1536 dimensions)
            limit: Maximum number of results to return (default: 5)
            similarity_threshold: Minimum similarity score (0-1) to include (default: 0.7)
            
        Returns:
            List of dictionaries containing conversation data and similarity scores,
            ordered by relevance (highest similarity first)
            
        Raises:
            MemorySystemError: If search operation fails
        """
        start_time = time.time()
        
        try:
            # Use Supabase RPC to perform vector similarity search
            # The RPC function should be created in Supabase to handle pgvector queries
            result = self.client.rpc(
                "match_conversations",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": similarity_threshold,
                    "match_count": limit
                }
            ).execute()
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            self.metrics_tracker.record_latency("memory.search_latency", elapsed_ms)
            
            if result.data is None:
                logger.warning(f"Semantic search returned no results (took {elapsed_ms:.2f}ms)")
                return []
            
            logger.debug(f"Semantic search returned {len(result.data)} results in {elapsed_ms:.2f}ms")
            
            # Log performance warning if exceeding target
            if elapsed_ms > 500:
                logger.warning(f"Semantic search exceeded 500ms target: {elapsed_ms:.2f}ms")
            
            return result.data
            
        except Exception as e:
            # If RPC function doesn't exist, fall back to manual query
            logger.warning(f"RPC search failed, using fallback method: {e}")
            try:
                # Fetch limited conversations for fallback (optimized limit)
                result = self.client.table("conversations").select("*").limit(50).execute()
                
                if not result.data:
                    return []
                
                # Compute cosine similarity for each conversation
                from numpy import dot
                from numpy.linalg import norm
                
                def cosine_similarity(a: List[float], b: List[float]) -> float:
                    """Calculate cosine similarity between two vectors."""
                    if not a or not b:
                        return 0.0
                    return float(dot(a, b) / (norm(a) * norm(b)))
                
                # Calculate similarities and filter
                results_with_similarity = []
                for conv in result.data:
                    if conv.get("embedding"):
                        similarity = cosine_similarity(query_embedding, conv["embedding"])
                        if similarity >= similarity_threshold:
                            conv["similarity"] = similarity
                            results_with_similarity.append(conv)
                
                # Sort by similarity (descending) and limit
                results_with_similarity.sort(key=lambda x: x["similarity"], reverse=True)
                
                elapsed_ms = (time.time() - start_time) * 1000
                
                # Record metrics
                self.metrics_tracker.record_latency("memory.search_latency", elapsed_ms)
                
                logger.debug(f"Fallback semantic search completed in {elapsed_ms:.2f}ms")
                
                if elapsed_ms > 500:
                    logger.warning(f"Fallback semantic search exceeded 500ms target: {elapsed_ms:.2f}ms")
                
                return results_with_similarity[:limit]
                
            except Exception as fallback_error:
                elapsed_ms = (time.time() - start_time) * 1000
                logger.error(f"Fallback semantic search failed after {elapsed_ms:.2f}ms: {fallback_error}")
                raise MemorySystemError(f"Semantic search failed: {fallback_error}")
    
    def get_personal_profile(self, user_id: str = "default_user") -> PersonalProfile:
        """Retrieve user preferences and learned behaviors.
        
        Uses in-memory caching to optimize performance for frequently accessed profiles.
        Cache TTL is 5 minutes to balance freshness and performance.
        
        Args:
            user_id: Unique identifier for the user (default: "default_user")
            
        Returns:
            PersonalProfile object with user preferences and settings
            
        Raises:
            MemorySystemError: If profile retrieval fails or profile doesn't exist
        """
        # Check cache first
        if user_id in self._profile_cache:
            cached_profile, cache_time = self._profile_cache[user_id]
            age = time.time() - cache_time
            
            if age < self._profile_cache_ttl:
                logger.debug(f"Retrieved profile for user {user_id} from cache (age: {age:.1f}s)")
                return cached_profile
            else:
                # Cache expired, remove it
                logger.debug(f"Profile cache expired for user {user_id} (age: {age:.1f}s)")
                del self._profile_cache[user_id]
        
        try:
            result = self.client.table("personal_profile").select("*").eq("user_id", user_id).execute()
            
            if not result.data or len(result.data) == 0:
                logger.warning(f"No profile found for user {user_id}, creating default profile")
                # Create default profile
                default_profile = PersonalProfile(
                    user_id=user_id,
                    first_name="Boss",
                    timezone="UTC",
                    preferences={},
                    habits={},
                    interests=[],
                    communication_style="casual",
                    work_hours={"start": "09:00", "end": "18:00"}
                )
                
                # Insert default profile
                profile_data = {
                    "user_id": user_id,
                    "first_name": default_profile.first_name,
                    "timezone": default_profile.timezone,
                    "preferences": default_profile.preferences,
                    "habits": default_profile.habits,
                    "interests": default_profile.interests,
                    "communication_style": default_profile.communication_style,
                    "work_hours": default_profile.work_hours,
                }
                self.client.table("personal_profile").insert(profile_data).execute()
                
                # Cache the default profile
                self._profile_cache[user_id] = (default_profile, time.time())
                
                return default_profile
            
            profile_data = result.data[0]
            
            # Convert database record to PersonalProfile object
            profile = PersonalProfile(
                user_id=profile_data["user_id"],
                first_name=profile_data["first_name"],
                timezone=profile_data["timezone"],
                preferences=profile_data.get("preferences", {}),
                habits=profile_data.get("habits", {}),
                interests=profile_data.get("interests", []),
                communication_style=profile_data.get("communication_style", "casual"),
                work_hours=profile_data.get("work_hours", {"start": "09:00", "end": "18:00"}),
            )
            
            # Cache the profile
            self._profile_cache[user_id] = (profile, time.time())
            
            logger.debug(f"Retrieved profile for user {user_id} from database")
            return profile
            
        except Exception as e:
            logger.error(f"Error retrieving personal profile: {e}")
            raise MemorySystemError(f"Failed to retrieve personal profile: {e}")
    
    def update_preference(
        self,
        user_id: str,
        key: str,
        value: Any
    ) -> None:
        """Update a user preference in the profile.
        
        This method updates a specific preference key in the user's profile.
        The preferences are stored as a JSONB field, allowing flexible key-value storage.
        
        Performance target: < 100ms
        
        Args:
            user_id: Unique identifier for the user
            key: Preference key to update
            value: New value for the preference
            
        Raises:
            MemorySystemError: If update operation fails
        """
        start_time = time.time()
        
        try:
            # First, get the current profile to merge preferences
            profile = self.get_personal_profile(user_id)
            
            # Update the preference
            profile.preferences[key] = value
            
            # Update the database
            result = self.client.table("personal_profile").update({
                "preferences": profile.preferences,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("user_id", user_id).execute()
            
            if not result.data:
                raise MemorySystemError(f"Failed to update preference: no data returned")
            
            # Invalidate cache to ensure fresh data on next read
            if user_id in self._profile_cache:
                del self._profile_cache[user_id]
            
            elapsed_ms = (time.time() - start_time) * 1000
            logger.debug(f"Updated preference '{key}' for user {user_id} in {elapsed_ms:.2f}ms")
            
            # Log performance warning if exceeding target
            if elapsed_ms > 100:
                logger.warning(f"Profile update exceeded 100ms target: {elapsed_ms:.2f}ms")
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"Error updating preference after {elapsed_ms:.2f}ms: {e}")
            raise MemorySystemError(f"Failed to update preference: {e}")
    
    def log_episodic_memory(
        self,
        interaction_type: str,
        context: str,
        action_taken: str,
        outcome: str,
        success: bool = True
    ) -> None:
        """Log an interaction with timestamp and outcome.
        
        Episodic memories provide a time-stamped log of all interactions,
        enabling JARVIS to learn from past experiences.
        
        Args:
            interaction_type: Type of interaction ("conversation", "tool_call", "hook")
            context: Contextual information about the interaction
            action_taken: Description of the action that was performed
            outcome: Description of the result or outcome
            success: Whether the interaction was successful (default: True)
            
        Raises:
            MemorySystemError: If logging operation fails
        """
        try:
            episodic_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "interaction_type": interaction_type,
                "context": context,
                "action_taken": action_taken,
                "outcome": outcome,
                "success": success,
            }
            
            result = self.client.table("episodic_memory").insert(episodic_data).execute()
            
            if not result.data:
                raise MemorySystemError("Failed to log episodic memory: no data returned")
            
            logger.debug(f"Logged episodic memory: {interaction_type}")
            
        except Exception as e:
            logger.error(f"Error logging episodic memory: {e}")
            raise MemorySystemError(f"Failed to log episodic memory: {e}")
    
    def inject_context(
        self,
        session_id: str,
        query_embedding: Optional[List[float]] = None,
        max_memories: int = 5
    ) -> str:
        """Generate context string from relevant memories.
        
        This method retrieves relevant past conversations and user profile information
        to inject into the system prompt for context-aware responses.
        
        Performance target: < 200ms
        Optimizations:
        - Uses cached profile data
        - Limits query results to essential data
        - Parallel-friendly query patterns
        
        Args:
            session_id: Current conversation session ID
            query_embedding: Optional embedding for semantic search of relevant memories
            max_memories: Maximum number of past memories to include (default: 5)
            
        Returns:
            Formatted context string ready for injection into system prompt
            
        Raises:
            MemorySystemError: If context generation fails
        """
        start_time = time.time()
        
        try:
            context_parts = []
            
            # Add user profile information (uses cache for performance)
            try:
                profile = self.get_personal_profile()
                context_parts.append("## User Profile")
                context_parts.append(f"Name: {profile.first_name}")
                context_parts.append(f"Timezone: {profile.timezone}")
                context_parts.append(f"Communication Style: {profile.communication_style}")
                
                if profile.preferences:
                    context_parts.append("\nPreferences:")
                    for key, value in profile.preferences.items():
                        context_parts.append(f"  - {key}: {value}")
                
                if profile.interests:
                    context_parts.append(f"\nInterests: {', '.join(profile.interests)}")
                
                context_parts.append("")  # Empty line for separation
            except Exception as e:
                logger.warning(f"Failed to load user profile for context: {e}")
            
            # Add relevant past conversations if embedding provided
            if query_embedding:
                try:
                    # Reduce limit for faster queries
                    relevant_memories = self.semantic_search(
                        query_embedding,
                        limit=min(max_memories, 3),  # Cap at 3 for performance
                        similarity_threshold=0.75  # Higher threshold for more relevant results
                    )
                    
                    if relevant_memories:
                        context_parts.append("## Relevant Past Conversations")
                        for i, memory in enumerate(relevant_memories, 1):
                            timestamp = memory.get("timestamp", "unknown")
                            user_input = memory.get("user_input", "")
                            response = memory.get("brain_response", "")
                            similarity = memory.get("similarity", 0)
                            
                            context_parts.append(f"\n### Memory {i} (similarity: {similarity:.2f})")
                            context_parts.append(f"Time: {timestamp}")
                            context_parts.append(f"User: {user_input}")
                            context_parts.append(f"Assistant: {response}")
                        
                        context_parts.append("")  # Empty line for separation
                except Exception as e:
                    logger.warning(f"Failed to load relevant memories for context: {e}")
            
            # Add recent session history (optimized query with limit)
            try:
                recent_conversations = self.client.table("conversations").select(
                    "timestamp, user_input, brain_response"
                ).eq("session_id", session_id).order(
                    "timestamp", desc=True
                ).limit(2).execute()  # Reduced from 3 to 2 for performance
                
                if recent_conversations.data:
                    context_parts.append("## Recent Session History")
                    for conv in reversed(recent_conversations.data):
                        timestamp = conv.get("timestamp", "unknown")
                        user_input = conv.get("user_input", "")
                        response = conv.get("brain_response", "")
                        
                        context_parts.append(f"\nTime: {timestamp}")
                        context_parts.append(f"User: {user_input}")
                        context_parts.append(f"Assistant: {response}")
                    
                    context_parts.append("")  # Empty line for separation
            except Exception as e:
                logger.warning(f"Failed to load recent session history: {e}")
            
            # Join all context parts
            context_string = "\n".join(context_parts)
            
            elapsed_ms = (time.time() - start_time) * 1000
            logger.debug(f"Generated context string with {len(context_parts)} parts in {elapsed_ms:.2f}ms")
            
            # Log performance warning if exceeding target
            if elapsed_ms > 200:
                logger.warning(f"Context injection exceeded 200ms target: {elapsed_ms:.2f}ms")
            
            return context_string
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"Error generating context after {elapsed_ms:.2f}ms: {e}")
            raise MemorySystemError(f"Failed to generate context: {e}")
    
    def clear_profile_cache(self, user_id: Optional[str] = None) -> None:
        """Clear the profile cache for a specific user or all users.
        
        This method is useful when you know a profile has been updated externally
        and want to force a fresh read from the database.
        
        Args:
            user_id: Optional user ID to clear. If None, clears all cached profiles.
        """
        if user_id:
            if user_id in self._profile_cache:
                del self._profile_cache[user_id]
                logger.debug(f"Cleared profile cache for user {user_id}")
        else:
            self._profile_cache.clear()
            logger.debug("Cleared all profile caches")
    
    def close(self) -> None:
        """Close the Supabase connection and cleanup resources.
        
        This method should be called when the Memory System is no longer needed
        to properly cleanup connections and resources.
        """
        try:
            # Clear caches
            self._profile_cache.clear()
            
            # Supabase client doesn't require explicit closing in Python SDK
            # but we log for consistency
            logger.info("Memory System closed and caches cleared")
        except Exception as e:
            logger.warning(f"Error during Memory System cleanup: {e}")
