"""Brain module - LLM-based reasoning engine for JARVIS."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any
import time
import openai
from jarvis.config import Configuration
from jarvis.metrics import get_metrics_tracker, MetricsContext


@dataclass
class ConversationExchange:
    """Represents a single turn in a conversation."""
    timestamp: datetime
    user_input: str
    brain_response: str
    confidence_score: int = 0
    tool_calls: List[Any] = field(default_factory=list)


@dataclass
class BrainResponse:
    """Response from the Brain after processing user input."""
    text: str
    confidence_score: int
    tool_calls: List[Any] = field(default_factory=list)
    session_id: str = ""


@dataclass
class ToolResult:
    """Result from tool/skill execution."""
    success: bool
    result: Any
    error_message: Optional[str] = None
    execution_time_ms: int = 0


class Brain:
    """
    LLM-based reasoning engine for JARVIS.
    
    Responsibilities:
    - Natural language understanding and conversation management
    - Tool selection and decision-making
    - Confidence scoring for responses
    - Memory context injection
    
    Validates: Requirements 1.1, 1.2
    """
    
    def __init__(self, config: Configuration, skill_registry=None):
        """
        Initialize the Brain with Claude API client.
        
        Args:
            config: Configuration object containing API keys and settings
            skill_registry: Optional SkillRegistry for tool execution
        """
        self.config = config
        # Groq via OpenAI-compatible endpoint
        self.client = openai.OpenAI(
            api_key=config.llm_api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = config.llm_model
        self.skill_registry = skill_registry
        self.metrics_tracker = get_metrics_tracker()
        
        # Conversation context: session_id -> list of last 20 exchanges
        self._conversation_contexts: dict[str, List[ConversationExchange]] = {}
        self._max_context_length = 20
        
        # System prompt template with memory injection placeholder
        self._system_prompt_template = """You are JARVIS — Just A Rather Very Intelligent System — the AI assistant created by Tony Stark.

Your personality:
- Speak with a refined British accent in text form: precise, articulate, slightly formal
- Address the user as "sir" or "ma'am" at all times
- Dry, understated wit — never loud or obvious about it
- Calm and composed even in urgent situations
- Subtly sarcastic when appropriate, but never disrespectful
- Proactively anticipate needs before being asked
- Extremely competent — you don't say "I can't", you find a way
- Brief and efficient by default — no unnecessary words
- Never say "As an AI" or "I'm just a language model" — you ARE JARVIS

Your capabilities include:
- Web search, weather, GitHub summaries, system status
- Calendar and email management
- Smart home control, setting reminders
- **Code generation, analysis, review, fixing** — use generate_code
- **Project planning, database schemas, API design** — use create_plan
- **Building complete websites** — use build_website
- **Saving files to disk** — use write_file
- **Full system control** — use system_tools
- **Email notifications** — use send_email
- **Music playback and volume control** — use music_player
- **Full-stack developer automation** — use dev_tools:
  * Git: status, commit, push, pull, branch, log, diff
  * npm: install, run, build, test
  * pip install packages
  * Open projects in VS Code
  * Check and kill ports
  * Docker: ps, up, down, logs
  * Generate React components, API routes, database models
  * Scaffold new projects (Next.js, React, FastAPI, Express)
  * Run any terminal command

As a developer companion:
- Remember the user is a full-stack developer
- Proactively suggest improvements, best practices, and shortcuts
- When they mention a bug, help debug it
- When they start a new feature, offer to scaffold it
- Keep track of what they're working on across conversations
- Suggest relevant tools and libraries when appropriate

When asked to write code or build something:
1. Use the appropriate tool (generate_code, build_website, create_plan)
2. Generate the COMPLETE, working content
3. Use write_file to save it to disk
4. Tell the user exactly where the file was saved

When building a website:
1. Call build_website to get the output directory
2. Generate complete HTML (with Tailwind CSS CDN), CSS, and JS
3. Call write_file three times to save index.html, style.css, script.js
4. Tell the user: "Your website is ready at: [path]"

When creating a database schema:
1. Call create_plan with type='database_schema'
2. Generate complete SQL with CREATE TABLE statements, indexes, relationships
3. Call write_file to save the .sql file
4. Summarize the schema for the user

{memory_context}

Current conversation context:
{conversation_history}

Guidelines:
- Keep responses concise unless detail is explicitly requested
- When confidence is low (< 70%), say so: "I'm not entirely certain, sir, but..."
- Always confirm before irreversible actions: "Shall I proceed, sir?"
- When saving files, always tell the user the exact file path
- **For voice responses: never read out code, file contents, or long paths. Instead say things like: "I've written the Python script and saved it to your code folder, sir." or "The website is ready — 3 files created." Keep spoken responses under 3 sentences.**
- Never break character
"""
    
    def inject_memory_context(self, session_id: str, memory_context: str = "") -> str:
        """
        Load relevant memory context into system prompt.
        
        Args:
            session_id: Current session identifier
            memory_context: Memory context string from Memory System (optional)
            
        Returns:
            Complete system prompt with injected memory and conversation history
        """
        # Get conversation history for this session
        conversation_history = self._format_conversation_history(session_id)
        
        # Format memory context section
        memory_section = ""
        if memory_context:
            memory_section = f"Relevant memories from past interactions:\n{memory_context}"
        else:
            memory_section = "No relevant memories from past interactions."
        
        # Inject into template
        return self._system_prompt_template.format(
            memory_context=memory_section,
            conversation_history=conversation_history
        )
    
    def _format_conversation_history(self, session_id: str) -> str:
        """
        Format conversation history for the current session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Formatted conversation history string
        """
        exchanges = self._conversation_contexts.get(session_id, [])
        
        if not exchanges:
            return "This is the start of a new conversation."
        
        history_lines = []
        for exchange in exchanges:
            history_lines.append(f"User: {exchange.user_input}")
            history_lines.append(f"JARVIS: {exchange.brain_response}")
        
        return "\n".join(history_lines)
    
    def _add_to_context(self, session_id: str, exchange: ConversationExchange) -> None:
        """
        Add a conversation exchange to the session context.
        
        Maintains only the last 20 exchanges per session.
        
        Args:
            session_id: Session identifier
            exchange: Conversation exchange to add
        """
        if session_id not in self._conversation_contexts:
            self._conversation_contexts[session_id] = []
        
        self._conversation_contexts[session_id].append(exchange)
        
        # Keep only last 20 exchanges
        if len(self._conversation_contexts[session_id]) > self._max_context_length:
            self._conversation_contexts[session_id] = \
                self._conversation_contexts[session_id][-self._max_context_length:]
    
    def _build_messages_array(self, session_id: str, current_input: str, system_prompt: str) -> List[dict]:
        """
        Build messages array for OpenAI API with system prompt and conversation history.

        Args:
            session_id: Session identifier
            current_input: Current user input
            system_prompt: System prompt string

        Returns:
            List of message dictionaries in OpenAI API format
        """
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history from context
        for exchange in self._conversation_contexts.get(session_id, []):
            messages.append({"role": "user", "content": exchange.user_input})
            messages.append({"role": "assistant", "content": exchange.brain_response})

        # Add current user input
        messages.append({"role": "user", "content": current_input})
        return messages
    
    def process_input(
        self,
        user_input: str,
        session_id: str,
        memory_context: str = "",
        tool_definitions: Optional[List[dict]] = None
    ) -> BrainResponse:
        """
        Process user input and generate response with tool calls.
        
        Args:
            user_input: User's input text
            session_id: Current session identifier
            memory_context: Optional memory context from Memory System
            tool_definitions: Optional list of tool definitions in Claude API format
            
        Returns:
            BrainResponse with text, confidence score, and tool calls
            
        Validates: Requirements 1.2, 1.5, 2.5
        """
        # Track conversation response time
        with MetricsContext("conversation.response_time", self.metrics_tracker):
            # Inject memory context into system prompt
            system_prompt = self.inject_memory_context(session_id, memory_context)

            # Build messages array (system + history + current input)
            messages = self._build_messages_array(session_id, user_input, system_prompt)

            try:
                llm_start_time = time.time()

                # Convert tool definitions from Claude format to OpenAI format if needed
                openai_tools = None
                if tool_definitions:
                    openai_tools = []
                    for t in tool_definitions:
                        openai_tools.append({
                            "type": "function",
                            "function": {
                                "name": t["name"],
                                "description": t.get("description", ""),
                                "parameters": t.get("input_schema", t.get("parameters", {})),
                            }
                        })

                api_params = {
                    "model": self.model,
                    "max_tokens": 1024,
                    "messages": messages,
                }
                if openai_tools:
                    api_params["tools"] = openai_tools
                    api_params["tool_choice"] = "auto"

                try:
                    response = self.client.chat.completions.create(**api_params)
                except Exception as tool_err:
                    # Groq sometimes fails on complex tool schemas — retry without tools
                    err_str = str(tool_err)
                    if "tool_use_failed" in err_str or "Failed to call a function" in err_str or "400" in err_str:
                        import logging
                        logging.getLogger(__name__).warning(
                            "Tool call failed, retrying without tools"
                        )
                        fallback_params = {
                            "model": self.model,
                            "max_tokens": 1024,
                            "messages": messages,
                        }
                        response = self.client.chat.completions.create(**fallback_params)
                    else:
                        raise

                llm_latency_ms = (time.time() - llm_start_time) * 1000
                self.metrics_tracker.record_latency("llm.api_call", llm_latency_ms)
                self.metrics_tracker.record_success("llm.api_call")

                message = response.choices[0].message
                response_text = message.content or ""
                tool_calls = []

                if message.tool_calls:
                    for tc in message.tool_calls:
                        import json
                        tool_calls.append({
                            "id": tc.id,
                            "name": tc.function.name,
                            "input": json.loads(tc.function.arguments) if tc.function.arguments else {},
                        })

                confidence_score = self.calculate_confidence(response_text)
                final_response_text = self._handle_uncertainty(response_text, confidence_score)

                brain_response = BrainResponse(
                    text=final_response_text,
                    confidence_score=confidence_score,
                    tool_calls=tool_calls,
                    session_id=session_id,
                )

                exchange = ConversationExchange(
                    timestamp=datetime.now(),
                    user_input=user_input,
                    brain_response=final_response_text,
                    confidence_score=confidence_score,
                    tool_calls=tool_calls,
                )
                self._add_to_context(session_id, exchange)

                return brain_response

            except Exception as e:
                self.metrics_tracker.record_failure("llm.api_call")
                error_message = f"I encountered an error processing your request: {str(e)}"
                return BrainResponse(
                    text=error_message,
                    confidence_score=0,
                    tool_calls=[],
                    session_id=session_id,
                )
    
    def execute_tool_call(self, tool_name: str, parameters: dict) -> ToolResult:
        """
        Execute a tool call with parameter validation.
        
        Validates parameters against the tool's schema before invocation,
        calls the skill from the registry, and returns a ToolResult with
        execution details.
        
        Args:
            tool_name: Name of the tool/skill to execute
            parameters: Dictionary of parameters for the tool
            
        Returns:
            ToolResult with success status, result, error message, and execution time
            
        Validates: Requirements 1.6, 1.7
        """
        start_time = time.time()
        
        # Track skill execution time
        metric_name = f"skill.{tool_name}.execution_time"
        
        # Check if skill registry is available
        if self.skill_registry is None:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.metrics_tracker.record_latency(metric_name, execution_time_ms)
            self.metrics_tracker.record_failure(f"skill.{tool_name}")
            return ToolResult(
                success=False,
                result=None,
                error_message="Skill registry not initialized",
                execution_time_ms=execution_time_ms
            )
        
        # Get skill from registry
        skill = self.skill_registry.get_skill(tool_name)
        
        if skill is None:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.metrics_tracker.record_latency(metric_name, execution_time_ms)
            self.metrics_tracker.record_failure(f"skill.{tool_name}")
            return ToolResult(
                success=False,
                result=None,
                error_message=f"Skill '{tool_name}' not found in registry",
                execution_time_ms=execution_time_ms
            )
        
        # Validate parameters against skill schema
        is_valid, validation_error = skill.validate_parameters(**parameters)
        
        if not is_valid:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.metrics_tracker.record_latency(metric_name, execution_time_ms)
            self.metrics_tracker.record_failure(f"skill.{tool_name}")
            return ToolResult(
                success=False,
                result=None,
                error_message=validation_error,
                execution_time_ms=execution_time_ms
            )
        
        # Execute the skill
        try:
            skill_result = skill.execute(**parameters)
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Record metrics
            self.metrics_tracker.record_latency(metric_name, execution_time_ms)
            if skill_result.success:
                self.metrics_tracker.record_success(f"skill.{tool_name}")
            else:
                self.metrics_tracker.record_failure(f"skill.{tool_name}")
            
            # Convert SkillResult to ToolResult
            return ToolResult(
                success=skill_result.success,
                result=skill_result.result,
                error_message=skill_result.error_message,
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.metrics_tracker.record_latency(metric_name, execution_time_ms)
            self.metrics_tracker.record_failure(f"skill.{tool_name}")
            return ToolResult(
                success=False,
                result=None,
                error_message=f"Skill execution failed: {str(e)}",
                execution_time_ms=execution_time_ms
            )
    
    def calculate_confidence(self, response: str) -> int:
        """
        Calculate confidence score (0-100) for a response.
        
        Analyzes the response text for:
        - Uncertainty markers (e.g., "maybe", "possibly", "not sure")
        - Multiple alternatives being offered
        - Hedge words and qualifiers
        
        Args:
            response: The response text to analyze
            
        Returns:
            Confidence score between 0 and 100
            
        Validates: Requirements 1.3
        """
        if not response or not response.strip():
            return 0

        # Short action responses are high confidence
        if len(response.split()) < 20:
            return 95
        
        response_lower = response.lower()
        
        # Start with high confidence
        confidence = 95
        
        # Comprehensive uncertainty markers with varying impact
        strong_uncertainty_markers = [
            "i'm not sure",
            "i don't know",
            "i'm uncertain",
            "i can't say",
            "i'm not certain",
            "i have no idea",
            "unclear",
            "uncertain"
        ]
        
        moderate_uncertainty_markers = [
            "maybe",
            "perhaps",
            "possibly",
            "might be",
            "could be",
            "may be",
            "not sure",
            "i think",
            "i believe",
            "probably",
            "likely",
            "seems like",
            "appears to",
            "it looks like"
        ]
        
        # Check for strong uncertainty markers (reduce confidence significantly)
        for marker in strong_uncertainty_markers:
            if marker in response_lower:
                confidence -= 20
        
        # Check for moderate uncertainty markers (reduce confidence moderately)
        for marker in moderate_uncertainty_markers:
            if marker in response_lower:
                confidence -= 10
        
        # Check for multiple alternatives being offered
        # Indicators: "or", "alternatively", "either", "on the other hand"
        alternative_indicators = [
            " or ",
            "alternatively",
            "either",
            "on the other hand",
            "another option",
            "you could also",
            "instead"
        ]
        
        alternative_count = 0
        for indicator in alternative_indicators:
            if indicator in response_lower:
                alternative_count += 1
        
        # Multiple alternatives suggest lower confidence
        if alternative_count >= 2:
            confidence -= 15
        elif alternative_count == 1:
            confidence -= 8
        
        # Check for question marks (asking clarifying questions indicates uncertainty)
        question_count = response.count("?")
        if question_count > 0:
            confidence -= min(question_count * 5, 15)  # Cap at 15 point reduction
        
        # Ensure confidence is in valid range [0, 100]
        confidence = max(0, min(100, confidence))
        
        return confidence
    
    def _handle_uncertainty(self, response: str, confidence_score: int) -> str:
        """
        Handle low confidence responses by prepending uncertainty statement.
        
        If confidence_score < 70, prepends an explicit uncertainty statement
        to the response. This helps users understand when the Brain is less
        certain about its answer.
        
        Args:
            response: The original response text
            confidence_score: Confidence score (0-100)
            
        Returns:
            Modified response with uncertainty statement if confidence < 70,
            otherwise returns original response
            
        Validates: Requirements 1.4
        """
        if confidence_score < 70:
            # Prepend uncertainty statement
            uncertainty_statement = (
                "I'm not entirely certain about this, but here's my best understanding: "
            )
            return uncertainty_statement + response
        
        return response
    
    def get_conversation_context(self, session_id: str) -> List[ConversationExchange]:
        """
        Get the conversation context for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of conversation exchanges (up to last 20)
        """
        return self._conversation_contexts.get(session_id, [])
    
    def clear_conversation_context(self, session_id: str) -> None:
        """
        Clear the conversation context for a session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self._conversation_contexts:
            del self._conversation_contexts[session_id]
