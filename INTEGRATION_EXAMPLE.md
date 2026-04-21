# Preference Learning Hook - Integration Example

## How to Integrate into Main Conversation Loop

The Preference Learning Hook should be triggered after every conversation turn in the main JARVIS conversation loop. Here's how to integrate it:

### Step 1: Initialize the Hook at Startup

```python
from jarvis.config import Configuration
from jarvis.brain.brain import Brain
from jarvis.memory.memory_system import MemorySystem
from jarvis.hooks.hooks_engine import HooksEngine
from jarvis.hooks.preference_learning_hook import create_preference_learning_hook

# Initialize components
config = Configuration(...)
brain = Brain(config)
memory_system = MemorySystem(config)
hooks_engine = HooksEngine()

# Create and register the preference learning hook
preference_learning_hook = create_preference_learning_hook(
    hooks_engine=hooks_engine,
    brain=brain,
    memory_system=memory_system,
    user_id="default_user"
)
```

### Step 2: Trigger After Each Conversation Turn

```python
def process_conversation_turn(user_input: str, session_id: str):
    """Process a single conversation turn with preference learning."""
    
    # Step 1: Get memory context
    memory_context = memory_system.inject_context(session_id)
    
    # Step 2: Process input through Brain
    brain_response = brain.process_input(
        user_input=user_input,
        session_id=session_id,
        memory_context=memory_context
    )
    
    # Step 3: Store conversation in memory
    from jarvis.memory.models import ConversationExchange
    from datetime import datetime
    
    exchange = ConversationExchange(
        timestamp=datetime.now(),
        user_input=user_input,
        brain_response=brain_response.text,
        confidence_score=brain_response.confidence_score,
        tool_calls=brain_response.tool_calls,
        embedding=[]  # Add embedding if available
    )
    memory_system.store_conversation(session_id, exchange)
    
    # Step 4: Trigger preference learning hook
    # This is the key integration point!
    hooks_engine.execute_hook("preference_learning")
    # Or call directly:
    preference_learning_hook.execute(
        user_input=user_input,
        brain_response=brain_response.text,
        session_id=session_id
    )
    
    return brain_response
```

### Step 3: Use in Voice Interface

```python
def voice_conversation_loop():
    """Main voice conversation loop with preference learning."""
    
    session_id = f"voice_session_{datetime.now().timestamp()}"
    
    while True:
        # Wait for wake word
        voice_interface.wait_for_wake_word()
        
        # Get voice input
        audio = voice_interface.record_audio()
        user_input = voice_interface.speech_to_text(audio)
        
        # Process conversation turn (includes preference learning)
        brain_response = process_conversation_turn(user_input, session_id)
        
        # Convert to speech and play
        audio_output = voice_interface.text_to_speech(brain_response.text)
        voice_interface.play_audio(audio_output)
```

### Step 4: Use in CLI Interface

```python
def cli_conversation_loop():
    """Main CLI conversation loop with preference learning."""
    
    session_id = f"cli_session_{datetime.now().timestamp()}"
    
    print("JARVIS CLI - Type 'exit' to quit")
    
    while True:
        # Get text input
        user_input = input("You: ")
        
        if user_input.lower() == "exit":
            break
        
        # Process conversation turn (includes preference learning)
        brain_response = process_conversation_turn(user_input, session_id)
        
        # Display response
        print(f"JARVIS: {brain_response.text}")
```

### Step 5: Use in Dashboard API

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/conversation/send", methods=["POST"])
def send_message():
    """API endpoint for dashboard conversation."""
    
    data = request.json
    user_input = data.get("message")
    session_id = data.get("session_id")
    
    # Process conversation turn (includes preference learning)
    brain_response = process_conversation_turn(user_input, session_id)
    
    return jsonify({
        "response": brain_response.text,
        "confidence": brain_response.confidence_score,
        "tool_calls": brain_response.tool_calls
    })
```

## Key Integration Points

### 1. After Brain.process_input()
The hook should be triggered **after** the Brain generates a response but **before** returning to the user. This ensures:
- The conversation is complete
- Both user input and brain response are available
- Learning happens in real-time

### 2. Before Returning Response
Trigger the hook before returning the response to the user:
```python
brain_response = brain.process_input(...)
preference_learning_hook.execute(...)  # Learn from this turn
return brain_response  # Then return to user
```

### 3. Asynchronous Option (Advanced)
For better performance, the hook can be triggered asynchronously:
```python
import threading

def trigger_learning_async(user_input, brain_response, session_id):
    """Trigger preference learning in background thread."""
    thread = threading.Thread(
        target=preference_learning_hook.execute,
        args=(user_input, brain_response, session_id)
    )
    thread.daemon = True
    thread.start()

# In conversation loop:
brain_response = brain.process_input(...)
trigger_learning_async(user_input, brain_response.text, session_id)
return brain_response  # Don't wait for learning to complete
```

## Error Handling

The hook includes comprehensive error handling, so failures won't break the conversation:

```python
try:
    preference_learning_hook.execute(user_input, brain_response.text, session_id)
except Exception as e:
    logger.error(f"Preference learning failed: {e}")
    # Continue conversation normally
```

## Performance Considerations

1. **LLM Call**: The hook makes an additional LLM call for analysis
   - Typical latency: 1-3 seconds
   - Consider async execution for better UX

2. **Database Updates**: Multiple preference updates per turn
   - Typical latency: 50-200ms total
   - Batching could improve performance

3. **Memory Impact**: Minimal (temporary session cleaned up)

## Monitoring

Track hook performance with logging:

```python
import time

start_time = time.time()
preference_learning_hook.execute(user_input, brain_response.text, session_id)
duration = time.time() - start_time

logger.info(f"Preference learning completed in {duration:.2f}s")
```

## Disabling the Hook

To disable preference learning temporarily:

```python
# Disable the hook
hooks_engine.disable_hook("preference_learning")

# Re-enable later
hooks_engine.enable_hook("preference_learning")
```

## Testing Integration

Test the integration with a simple script:

```python
def test_preference_learning_integration():
    """Test preference learning in conversation flow."""
    
    # Setup
    session_id = "test_session"
    
    # Simulate conversation
    user_input = "I prefer to be called Alex"
    brain_response = brain.process_input(user_input, session_id)
    
    # Trigger learning
    preference_learning_hook.execute(
        user_input=user_input,
        brain_response=brain_response.text,
        session_id=session_id
    )
    
    # Verify profile updated
    profile = memory_system.get_personal_profile()
    assert any("alex" in str(v).lower() for v in profile.preferences.values())
    
    print("✓ Preference learning integration test passed")

test_preference_learning_integration()
```

## Summary

The Preference Learning Hook integrates seamlessly into any conversation loop:
1. Initialize once at startup
2. Trigger after each Brain.process_input() call
3. Hook handles extraction, storage, and logging automatically
4. Errors are handled gracefully without breaking conversation flow
5. Can be disabled/enabled dynamically via HooksEngine

The hook is designed to be non-intrusive and fail-safe, ensuring JARVIS continues to function even if preference learning encounters issues.
