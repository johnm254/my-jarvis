# JARVIS CLI Interface

A command-line interface for text-based interaction with JARVIS, your personal AI assistant.

## Features

- **Text-based conversation**: Chat with JARVIS through a simple command-line interface
- **Brain integration**: Connects directly to the Brain reasoning engine
- **Memory context**: Maintains conversation history and injects relevant context
- **Special commands**: Built-in commands for managing your session
- **Error handling**: Graceful error handling with informative messages
- **Session management**: Each CLI session has a unique ID for tracking

## Usage

### Running the CLI

There are three ways to start the JARVIS CLI:

1. **Using the module flag** (recommended):
   ```bash
   python -m jarvis.cli
   ```

2. **Using the standalone script**:
   ```bash
   python jarvis_cli.py
   ```

3. **Importing and running programmatically**:
   ```python
   from jarvis.cli import CLIInterface
   
   cli = CLIInterface()
   cli.run()
   ```

### Available Commands

Once the CLI is running, you can use the following commands:

- `/help` - Display help information about available commands
- `/history` - Show conversation history for the current session
- `/clear` - Clear the terminal screen
- `/exit` - Exit JARVIS and end the session

### Example Session

```
==============================================================
  JARVIS - Personal AI Assistant
==============================================================

Welcome! I'm JARVIS, your personal AI assistant.
Type your message and press Enter to chat with me.

Available commands:
  /help     - Show available commands
  /history  - Show conversation history
  /clear    - Clear the screen
  /exit     - Exit JARVIS

--------------------------------------------------------------

You: Hello JARVIS!

JARVIS: Hello Boss! How can I assist you today?

You: What's the weather like?

JARVIS: I'd be happy to help you check the weather. However, I need to know your location. Could you please tell me which city you'd like the weather for?

You: /history

==============================================================
  Conversation History
==============================================================

[14:23:15] Exchange 1
You: Hello JARVIS!
JARVIS: Hello Boss! How can I assist you today?
(Confidence: 95%)

[14:23:42] Exchange 2
You: What's the weather like?
JARVIS: I'd be happy to help you check the weather. However, I need to know your location. Could you please tell me which city you'd like the weather for?
(Confidence: 85%)

--------------------------------------------------------------

You: /exit

Goodbye! Have a great day, Boss.
```

## Configuration

The CLI uses the standard JARVIS configuration from environment variables or `.env` file. Required configuration:

- `LLM_API_KEY` - API key for the LLM (Claude)
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase API key
- `JWT_SECRET` - Secret for JWT authentication

See `.env.example` for a complete list of configuration options.

## Architecture

The CLI interface consists of:

- **CLIInterface**: Main class that manages the interactive session
- **Brain integration**: Processes user input through the Brain reasoning engine
- **Memory integration**: Stores conversations and retrieves context
- **Command handling**: Processes special commands (/exit, /history, etc.)
- **Error handling**: Gracefully handles errors and provides user feedback

## Error Handling

The CLI handles various error scenarios:

- **Initialization errors**: If Brain or Memory System fails to initialize, displays error and exits
- **Processing errors**: If Brain fails to process input, displays error and allows retry
- **Memory errors**: If memory operations fail, continues without memory context
- **Keyboard interrupts**: Handles Ctrl+C gracefully without exiting
- **EOF**: Handles Ctrl+D to exit cleanly

## Development

### Adding New Commands

To add a new command:

1. Add the command handling logic to `handle_command()` method
2. Update the help text in `display_help()` method
3. Update the welcome message in `display_welcome()` if needed

Example:
```python
def handle_command(self, command: str) -> bool:
    command = command.lower().strip()
    
    if command == "/mycommand":
        # Your command logic here
        print("Executing my command...")
        return True
    
    # ... rest of the commands
```

### Testing

To test the CLI without running the interactive loop:

```python
from jarvis.cli import CLIInterface

# Create CLI instance
cli = CLIInterface()

# Test individual methods
cli.display_help()
cli.display_history()
cli.clear_screen()
```

## Troubleshooting

### "Failed to initialize JARVIS"

This error occurs when the Brain or Memory System cannot be initialized. Check:
- Your `.env` file has all required configuration
- Your API keys are valid
- Your Supabase instance is accessible

### "Error processing input"

This error occurs when the Brain fails to process your input. Check:
- Your LLM API key is valid and has credits
- Your network connection is stable
- The Brain service is running correctly

### Memory warnings

If you see warnings about memory operations failing, the CLI will continue to work but without conversation history persistence. Check:
- Your Supabase connection is working
- Your database schema is properly initialized

## Related Documentation

- [Brain Module](../brain/README.md) - LLM reasoning engine
- [Memory System](../memory/README.md) - Persistent storage
- [Configuration](../config.py) - Configuration management
- [Main README](../../README.md) - Overall JARVIS documentation
