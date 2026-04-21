"""CLI interface for text-based interaction with JARVIS.

This module provides a command-line interface for interacting with JARVIS
through text input. It supports conversation with the Brain and special
commands for managing the session.

Validates: Requirements 3.7
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional
from uuid import uuid4

from jarvis.brain.brain import Brain
from jarvis.config import Configuration, load_config
from jarvis.memory.memory_system import MemorySystem

logger = logging.getLogger(__name__)


class CLIInterface:
    """Command-line interface for JARVIS text interaction.
    
    Provides a simple text-based interface with:
    - Input prompt for user messages
    - Display of Brain responses
    - Special commands: /exit, /history, /clear, /help
    - Error handling and graceful degradation
    
    Attributes:
        brain: Brain instance for processing input
        memory: MemorySystem instance for context and history
        session_id: Unique identifier for the current session
        config: Configuration object
        running: Flag indicating if the CLI is active
    """
    
    def __init__(self, config: Optional[Configuration] = None):
        """Initialize the CLI interface.
        
        Args:
            config: Optional Configuration object. If not provided, loads from environment.
        """
        self.config = config or load_config()
        self.session_id = str(uuid4())
        self.running = False
        
        # Initialize Brain and Memory System
        try:
            self.memory = MemorySystem(self.config)
            self.brain = Brain(self.config)
            logger.info(f"CLI initialized with session ID: {self.session_id}")
        except Exception as e:
            logger.error(f"Failed to initialize CLI: {e}")
            print(f"Error: Failed to initialize JARVIS: {e}")
            print("Please check your configuration and try again.")
            sys.exit(1)
    
    def display_welcome(self) -> None:
        """Display welcome message and instructions."""
        print("\n" + "=" * 60)
        print("  JARVIS - Personal AI Assistant")
        print("=" * 60)
        print("\nWelcome! I'm JARVIS, your personal AI assistant.")
        print("Type your message and press Enter to chat with me.")
        print("\nAvailable commands:")
        print("  /help     - Show available commands")
        print("  /history  - Show conversation history")
        print("  /clear    - Clear the screen")
        print("  /exit     - Exit JARVIS")
        print("\n" + "-" * 60 + "\n")
    
    def display_help(self) -> None:
        """Display help information about available commands."""
        print("\n" + "=" * 60)
        print("  JARVIS Commands")
        print("=" * 60)
        print("\nAvailable commands:")
        print("  /help     - Show this help message")
        print("  /history  - Display conversation history for this session")
        print("  /clear    - Clear the terminal screen")
        print("  /exit     - Exit JARVIS and end the session")
        print("\nTo chat with JARVIS, simply type your message and press Enter.")
        print("Examples:")
        print("  - What's the weather like today?")
        print("  - Tell me a joke")
        print("  - Help me with a Python problem")
        print("\n" + "-" * 60 + "\n")
    
    def display_history(self) -> None:
        """Display conversation history for the current session."""
        try:
            # Get conversation context from Brain
            exchanges = self.brain.get_conversation_context(self.session_id)
            
            if not exchanges:
                print("\nNo conversation history yet. Start chatting to build history!\n")
                return
            
            print("\n" + "=" * 60)
            print("  Conversation History")
            print("=" * 60 + "\n")
            
            for i, exchange in enumerate(exchanges, 1):
                timestamp = exchange.timestamp.strftime("%H:%M:%S")
                print(f"[{timestamp}] Exchange {i}")
                print(f"You: {exchange.user_input}")
                print(f"JARVIS: {exchange.brain_response}")
                if exchange.confidence_score > 0:
                    print(f"(Confidence: {exchange.confidence_score}%)")
                print()
            
            print("-" * 60 + "\n")
            
        except Exception as e:
            logger.error(f"Error displaying history: {e}")
            print(f"\nError: Failed to retrieve conversation history: {e}\n")
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        # Use appropriate clear command based on OS
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "=" * 60)
        print("  JARVIS - Personal AI Assistant")
        print("=" * 60 + "\n")
    
    def handle_command(self, command: str) -> bool:
        """Handle special commands.
        
        Args:
            command: The command string (e.g., "/exit", "/help")
            
        Returns:
            True if the CLI should continue running, False if it should exit
        """
        command = command.lower().strip()
        
        if command == "/exit":
            print("\nGoodbye! Have a great day, Boss.\n")
            return False
        
        elif command == "/help":
            self.display_help()
        
        elif command == "/history":
            self.display_history()
        
        elif command == "/clear":
            self.clear_screen()
        
        else:
            print(f"\nUnknown command: {command}")
            print("Type /help to see available commands.\n")
        
        return True
    
    def process_user_input(self, user_input: str) -> None:
        """Process user input through the Brain and display response.
        
        Args:
            user_input: The user's input text
        """
        try:
            # Get memory context for this session
            memory_context = ""
            try:
                memory_context = self.memory.inject_context(self.session_id)
            except Exception as e:
                logger.warning(f"Failed to inject memory context: {e}")
                # Continue without memory context
            
            # Process input through Brain
            response = self.brain.process_input(
                user_input=user_input,
                session_id=self.session_id,
                memory_context=memory_context
            )
            
            # Display response
            print(f"\nJARVIS: {response.text}")
            
            # Display confidence score if low
            if response.confidence_score < 70:
                print(f"(Confidence: {response.confidence_score}%)")
            
            # Display tool calls if any
            if response.tool_calls:
                print(f"\n[Used {len(response.tool_calls)} tool(s)]")
            
            print()
            
            # Store conversation in memory
            try:
                from jarvis.memory.models import ConversationExchange
                
                exchange = ConversationExchange(
                    timestamp=datetime.now(),
                    user_input=user_input,
                    brain_response=response.text,
                    confidence_score=response.confidence_score,
                    tool_calls=response.tool_calls,
                    embedding=[]  # Embedding would be generated separately
                )
                
                self.memory.store_conversation(self.session_id, exchange)
            except Exception as e:
                logger.warning(f"Failed to store conversation in memory: {e}")
                # Continue without storing
            
        except KeyboardInterrupt:
            raise  # Re-raise to handle in main loop
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            print(f"\nError: I encountered an issue processing your request: {e}")
            print("Please try again or rephrase your question.\n")
    
    def run(self) -> None:
        """Run the CLI main loop.
        
        This method starts the interactive CLI session and handles user input
        until the user exits with /exit or Ctrl+C.
        """
        self.running = True
        self.display_welcome()
        
        try:
            while self.running:
                try:
                    # Display prompt and get user input
                    user_input = input("You: ").strip()
                    
                    # Skip empty input
                    if not user_input:
                        continue
                    
                    # Check if it's a command
                    if user_input.startswith("/"):
                        self.running = self.handle_command(user_input)
                    else:
                        # Process regular input through Brain
                        self.process_user_input(user_input)
                
                except KeyboardInterrupt:
                    print("\n\nInterrupted. Type /exit to quit or continue chatting.\n")
                    continue
                
                except EOFError:
                    # Handle Ctrl+D (EOF)
                    print("\n\nGoodbye! Have a great day, Boss.\n")
                    break
        
        finally:
            # Cleanup
            try:
                self.memory.close()
                logger.info(f"CLI session ended: {self.session_id}")
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")


def main():
    """Main entry point for the CLI interface."""
    try:
        cli = CLIInterface()
        cli.run()
    except Exception as e:
        logger.error(f"Fatal error in CLI: {e}")
        print(f"\nFatal error: {e}")
        print("JARVIS CLI has terminated unexpectedly.")
        sys.exit(1)


if __name__ == "__main__":
    main()
