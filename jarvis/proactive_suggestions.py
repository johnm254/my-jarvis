"""Proactive suggestion system for JARVIS.

This module analyzes user behavior patterns and generates proactive suggestions
for optimizations, automations, and improvements.

Validates: Requirements 20.1, 20.2, 20.3
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from jarvis.memory.memory_system import MemorySystem
from jarvis.brain.brain import Brain

logger = logging.getLogger(__name__)


class ProactiveSuggestion:
    """Represents a proactive suggestion."""
    
    def __init__(
        self,
        suggestion_type: str,
        title: str,
        description: str,
        confidence: int,
        action: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a proactive suggestion.
        
        Args:
            suggestion_type: Type of suggestion (automation, optimization, reminder)
            title: Short title for the suggestion
            description: Detailed description
            confidence: Confidence score (0-100)
            action: Optional action to take if user accepts
        """
        self.suggestion_type = suggestion_type
        self.title = title
        self.description = description
        self.confidence = confidence
        self.action = action or {}
        self.created_at = datetime.utcnow()


class ProactiveSuggestionEngine:
    """
    Engine for generating proactive suggestions based on user behavior.
    
    Analyzes:
    - Usage patterns in Personal_Profile
    - Episodic memory for repeated actions
    - Conversation history for optimization opportunities
    
    Validates: Requirements 20.1, 20.2, 20.3
    """
    
    def __init__(self, memory_system: MemorySystem, brain: Brain):
        """
        Initialize the proactive suggestion engine.
        
        Args:
            memory_system: MemorySystem instance for data access
            brain: Brain instance for generating suggestions
        """
        self.memory_system = memory_system
        self.brain = brain
    
    def generate_suggestions(self, user_id: str = "default_user") -> List[ProactiveSuggestion]:
        """
        Generate proactive suggestions for the user.
        
        Args:
            user_id: User ID to generate suggestions for
            
        Returns:
            List of ProactiveSuggestion objects with confidence > 80
        """
        suggestions = []
        
        try:
            # Get user profile
            profile = self.memory_system.get_personal_profile(user_id)
            
            # Analyze preferences for optimization opportunities
            suggestions.extend(self._analyze_preferences(profile))
            
            # Analyze episodic memory for patterns
            suggestions.extend(self._analyze_episodic_patterns(user_id))
            
            # Analyze conversation patterns
            suggestions.extend(self._analyze_conversation_patterns(user_id))
            
            # Filter suggestions by confidence threshold (> 80)
            high_confidence_suggestions = [
                s for s in suggestions if s.confidence > 80
            ]
            
            return high_confidence_suggestions
            
        except Exception as e:
            logger.error(f"Error generating proactive suggestions: {e}")
            return []
    
    def _analyze_preferences(self, profile) -> List[ProactiveSuggestion]:
        """
        Analyze user preferences for optimization opportunities.
        
        Args:
            profile: PersonalProfile object
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Check if user has set timezone but not work hours
        if profile.timezone != "UTC" and not profile.work_hours:
            suggestions.append(ProactiveSuggestion(
                suggestion_type="optimization",
                title="Set your work hours",
                description="I notice you've set your timezone. Would you like to configure your work hours so I can adjust my communication style accordingly?",
                confidence=85,
                action={"type": "prompt_work_hours"}
            ))
        
        # Check if user has interests but no related automations
        if profile.interests and len(profile.interests) > 0:
            suggestions.append(ProactiveSuggestion(
                suggestion_type="automation",
                title="Create news automation",
                description=f"Based on your interests in {', '.join(profile.interests[:3])}, I could set up a daily news brief with relevant articles. Would you like that?",
                confidence=82,
                action={"type": "create_news_automation", "interests": profile.interests}
            ))
        
        return suggestions
    
    def _analyze_episodic_patterns(self, user_id: str) -> List[ProactiveSuggestion]:
        """
        Analyze episodic memory for repeated action patterns.
        
        Args:
            user_id: User ID
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        try:
            # Get recent episodic memories (last 7 days)
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            
            result = self.memory_system.client.table("episodic_memory").select(
                "interaction_type, context, action_taken"
            ).gte("timestamp", week_ago).execute()
            
            if result.data and len(result.data) > 10:
                # Analyze for repeated patterns
                action_counts = {}
                for memory in result.data:
                    action = memory.get('action_taken', '')
                    action_counts[action] = action_counts.get(action, 0) + 1
                
                # Find frequently repeated actions
                for action, count in action_counts.items():
                    if count >= 3:  # Repeated 3+ times in a week
                        suggestions.append(ProactiveSuggestion(
                            suggestion_type="automation",
                            title=f"Automate repeated action",
                            description=f"I notice you've performed '{action}' {count} times this week. Would you like me to create an automation for this?",
                            confidence=88,
                            action={"type": "create_automation", "action": action}
                        ))
        
        except Exception as e:
            logger.warning(f"Error analyzing episodic patterns: {e}")
        
        return suggestions
    
    def _analyze_conversation_patterns(self, user_id: str) -> List[ProactiveSuggestion]:
        """
        Analyze conversation history for optimization opportunities.
        
        Args:
            user_id: User ID
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        try:
            # Get recent conversations with low confidence scores
            result = self.memory_system.client.table("conversations").select(
                "user_input, confidence_score"
            ).lt("confidence_score", 70).limit(10).execute()
            
            if result.data and len(result.data) >= 3:
                suggestions.append(ProactiveSuggestion(
                    suggestion_type="optimization",
                    title="Improve response accuracy",
                    description="I've noticed some of my recent responses had lower confidence. Would you like to provide feedback to help me improve?",
                    confidence=81,
                    action={"type": "request_feedback"}
                ))
        
        except Exception as e:
            logger.warning(f"Error analyzing conversation patterns: {e}")
        
        return suggestions
    
    def generate_weekly_summary(self, user_id: str = "default_user") -> str:
        """
        Generate a weekly summary of learned preferences and suggestions.
        
        Args:
            user_id: User ID
            
        Returns:
            Formatted summary string
        """
        try:
            profile = self.memory_system.get_personal_profile(user_id)
            suggestions = self.generate_suggestions(user_id)
            
            # Get conversation count for the week
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            conversations = self.memory_system.client.table("conversations").select(
                "id"
            ).gte("timestamp", week_ago).execute()
            
            conversation_count = len(conversations.data) if conversations.data else 0
            
            # Build summary
            summary_parts = [
                "# Weekly Summary",
                "",
                f"## Activity",
                f"- Conversations this week: {conversation_count}",
                f"- Current preferences: {len(profile.preferences)}",
                f"- Interests tracked: {len(profile.interests)}",
                "",
            ]
            
            if suggestions:
                summary_parts.append("## Proactive Suggestions")
                for i, suggestion in enumerate(suggestions[:5], 1):
                    summary_parts.append(f"{i}. **{suggestion.title}** (confidence: {suggestion.confidence}%)")
                    summary_parts.append(f"   {suggestion.description}")
                    summary_parts.append("")
            else:
                summary_parts.append("## Proactive Suggestions")
                summary_parts.append("No new suggestions this week. Keep up the great work!")
                summary_parts.append("")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating weekly summary: {e}")
            return "Unable to generate weekly summary at this time."


# Global suggestion engine instance (initialized lazily)
_suggestion_engine: Optional[ProactiveSuggestionEngine] = None


def get_suggestion_engine(memory_system: MemorySystem, brain: Brain) -> ProactiveSuggestionEngine:
    """
    Get or create the global suggestion engine instance.
    
    Args:
        memory_system: MemorySystem instance
        brain: Brain instance
        
    Returns:
        ProactiveSuggestionEngine instance
    """
    global _suggestion_engine
    if _suggestion_engine is None:
        _suggestion_engine = ProactiveSuggestionEngine(memory_system, brain)
    return _suggestion_engine
