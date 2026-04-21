"""Preference Learning Hook for JARVIS - Learns from every conversation turn.

Validates: Requirements 15.1, 15.2, 15.3, 15.4
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class PreferenceLearningHook:
    """
    Preference learning hook that executes after every conversation turn.
    
    Analyzes user input and brain response to extract:
    - User preferences (likes, dislikes, habits)
    - Corrections (when user corrects JARVIS)
    - New facts about the user (interests, work hours, etc.)
    
    Updates Personal_Profile with extracted information to personalize
    future interactions.
    
    Validates: Requirements 15.1, 15.2, 15.3, 15.4
    """
    
    def __init__(
        self,
        brain,
        memory_system,
        user_id: str = "default_user"
    ):
        """
        Initialize the preference learning hook.
        
        Args:
            brain: Brain instance for LLM-based preference extraction
            memory_system: MemorySystem instance for updating preferences
            user_id: User ID for updating preferences (default: "default_user")
        """
        self._brain = brain
        self._memory_system = memory_system
        self._user_id = user_id
        
        logger.info("PreferenceLearningHook initialized")
    
    def execute(
        self,
        user_input: str,
        brain_response: str,
        session_id: str
    ) -> None:
        """
        Execute the preference learning hook after a conversation turn.
        
        Analyzes the conversation exchange to extract preferences, corrections,
        and new facts, then updates the Personal_Profile.
        
        Args:
            user_input: The user's input text
            brain_response: The brain's response text
            session_id: Current conversation session ID
            
        Validates: Requirements 15.1, 15.2, 15.3, 15.4
        """
        try:
            logger.debug(
                f"Executing preference learning hook for session {session_id}"
            )
            
            # Step 1: Analyze the conversation to extract learnings
            learnings = self._extract_learnings(user_input, brain_response)
            
            if not learnings:
                logger.debug("No learnings extracted from this conversation turn")
                return
            
            # Step 2: Update Personal_Profile with extracted learnings
            self._update_profile(learnings)
            
            # Step 3: Log the learning to episodic memory
            self._log_learning(user_input, brain_response, learnings)
            
            logger.info(
                f"Preference learning completed: "
                f"{len(learnings.get('preferences', []))} preferences, "
                f"{len(learnings.get('corrections', []))} corrections, "
                f"{len(learnings.get('facts', []))} facts"
            )
            
        except Exception as e:
            logger.error(
                f"Preference learning hook execution failed: {e}",
                exc_info=True
            )
    
    def _extract_learnings(
        self,
        user_input: str,
        brain_response: str
    ) -> Dict[str, Any]:
        """
        Use the Brain/LLM to extract learnings from the conversation.
        
        Analyzes the conversation exchange to identify:
        - Preferences: User likes, dislikes, habits
        - Corrections: When user corrects JARVIS
        - Facts: New information about the user
        
        Args:
            user_input: The user's input text
            brain_response: The brain's response text
            
        Returns:
            Dictionary with extracted learnings:
            {
                "preferences": [{"key": "...", "value": "...", "category": "..."}],
                "corrections": [{"original": "...", "corrected": "...", "context": "..."}],
                "facts": [{"key": "...", "value": "...", "category": "..."}]
            }
        """
        try:
            # Create a specialized prompt for preference extraction
            extraction_prompt = f"""Analyze this conversation exchange and extract any learnings about the user.

User Input: {user_input}
Assistant Response: {brain_response}

Extract the following types of information:

1. **Preferences**: User likes, dislikes, habits, or preferences
   - Examples: "I prefer coffee over tea", "I don't like mornings", "I usually work from home"
   
2. **Corrections**: When the user corrects the assistant
   - Examples: "Actually, my name is John", "No, I meant tomorrow not today"
   
3. **Facts**: New factual information about the user
   - Examples: "I live in Seattle", "I work as a software engineer", "My work hours are 9-5"

Return your analysis as a JSON object with this structure:
{{
  "preferences": [
    {{"key": "preference_name", "value": "preference_value", "category": "likes|dislikes|habits"}}
  ],
  "corrections": [
    {{"original": "what_was_wrong", "corrected": "what_is_correct", "context": "brief_context"}}
  ],
  "facts": [
    {{"key": "fact_name", "value": "fact_value", "category": "personal|work|location|interests"}}
  ]
}}

If no learnings are found in any category, return an empty array for that category.
Only extract clear, explicit information. Do not infer or assume.
Return ONLY the JSON object, no additional text."""

            # Call the Brain to extract learnings
            # Use a temporary session for this analysis
            analysis_session = f"preference_learning_{datetime.now().timestamp()}"
            
            response = self._brain.process_input(
                user_input=extraction_prompt,
                session_id=analysis_session,
                memory_context=""  # No memory context needed for extraction
            )
            
            # Parse the JSON response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove ```
            
            response_text = response_text.strip()
            
            # Parse JSON
            learnings = json.loads(response_text)
            
            # Validate structure
            if not isinstance(learnings, dict):
                logger.warning("Learnings extraction returned non-dict, ignoring")
                return {}
            
            # Ensure all expected keys exist
            learnings.setdefault("preferences", [])
            learnings.setdefault("corrections", [])
            learnings.setdefault("facts", [])
            
            # Clean up the temporary session from brain context
            self._brain.clear_conversation_context(analysis_session)
            
            return learnings
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse learnings JSON: {e}")
            logger.debug(f"Response text: {response_text}")
            return {}
        except Exception as e:
            logger.error(f"Failed to extract learnings: {e}", exc_info=True)
            return {}
    
    def _update_profile(self, learnings: Dict[str, Any]) -> None:
        """
        Update the Personal_Profile with extracted learnings.
        
        Args:
            learnings: Dictionary with preferences, corrections, and facts
        """
        try:
            # Update preferences
            for pref in learnings.get("preferences", []):
                key = pref.get("key")
                value = pref.get("value")
                category = pref.get("category", "general")
                
                if key and value:
                    # Store preference with category prefix
                    pref_key = f"preference_{category}_{key}"
                    self._memory_system.update_preference(
                        self._user_id,
                        pref_key,
                        value
                    )
                    logger.debug(f"Updated preference: {pref_key} = {value}")
            
            # Update corrections (store as preferences to avoid repeating mistakes)
            for correction in learnings.get("corrections", []):
                original = correction.get("original")
                corrected = correction.get("corrected")
                context = correction.get("context", "")
                
                if original and corrected:
                    # Store correction with timestamp
                    correction_key = f"correction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    correction_value = {
                        "original": original,
                        "corrected": corrected,
                        "context": context,
                        "timestamp": datetime.now().isoformat()
                    }
                    self._memory_system.update_preference(
                        self._user_id,
                        correction_key,
                        correction_value
                    )
                    logger.debug(f"Stored correction: {original} -> {corrected}")
            
            # Update facts
            for fact in learnings.get("facts", []):
                key = fact.get("key")
                value = fact.get("value")
                category = fact.get("category", "general")
                
                if key and value:
                    # Store fact with category prefix
                    fact_key = f"fact_{category}_{key}"
                    self._memory_system.update_preference(
                        self._user_id,
                        fact_key,
                        value
                    )
                    logger.debug(f"Updated fact: {fact_key} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to update profile: {e}", exc_info=True)
    
    def _log_learning(
        self,
        user_input: str,
        brain_response: str,
        learnings: Dict[str, Any]
    ) -> None:
        """
        Log the learning event to episodic memory.
        
        Args:
            user_input: The user's input text
            brain_response: The brain's response text
            learnings: Dictionary with extracted learnings
        """
        try:
            # Count learnings
            pref_count = len(learnings.get("preferences", []))
            corr_count = len(learnings.get("corrections", []))
            fact_count = len(learnings.get("facts", []))
            
            total_count = pref_count + corr_count + fact_count
            
            if total_count == 0:
                return  # Don't log if nothing was learned
            
            # Create context summary
            context = f"User: {user_input[:100]}..."
            
            # Create action summary
            action_taken = (
                f"Extracted {pref_count} preferences, "
                f"{corr_count} corrections, {fact_count} facts"
            )
            
            # Create outcome summary
            outcome_parts = []
            if pref_count > 0:
                outcome_parts.append(f"{pref_count} preferences updated")
            if corr_count > 0:
                outcome_parts.append(f"{corr_count} corrections stored")
            if fact_count > 0:
                outcome_parts.append(f"{fact_count} facts learned")
            
            outcome = ", ".join(outcome_parts)
            
            # Log to episodic memory
            self._memory_system.log_episodic_memory(
                interaction_type="preference_learning",
                context=context,
                action_taken=action_taken,
                outcome=outcome,
                success=True
            )
            
            logger.debug(f"Logged learning event: {outcome}")
            
        except Exception as e:
            logger.error(f"Failed to log learning: {e}", exc_info=True)


def create_preference_learning_hook(
    hooks_engine,
    brain,
    memory_system,
    user_id: str = "default_user"
):
    """
    Create and register the preference learning hook with the hooks engine.
    
    This hook is event-based and should be triggered after every conversation turn.
    Unlike time-based hooks, it's not scheduled but called explicitly after
    each Brain.process_input() call.
    
    Args:
        hooks_engine: HooksEngine instance to register the hook with
        brain: Brain instance for LLM-based preference extraction
        memory_system: MemorySystem instance for updating preferences
        user_id: User ID for updating preferences (default: "default_user")
        
    Returns:
        The created PreferenceLearningHook instance
        
    Validates: Requirements 15.1, 15.2, 15.3, 15.4
    """
    from jarvis.hooks.hooks_engine import Hook
    
    # Create the preference learning hook instance
    preference_learning = PreferenceLearningHook(
        brain=brain,
        memory_system=memory_system,
        user_id=user_id
    )
    
    # Create the hook as an event-based hook
    # Event-based hooks are not scheduled, they're triggered manually
    hook = Hook(
        id="preference_learning",
        name="Preference Learning",
        description="Learns from every conversation turn to extract preferences, corrections, and facts",
        hook_type="event",
        trigger="after_conversation_turn",  # Event name
        callback=preference_learning.execute,
        enabled=True
    )
    
    # Register with hooks engine
    hooks_engine.register_hook(hook)
    
    logger.info("Preference learning hook registered as event-based hook")
    
    return preference_learning
