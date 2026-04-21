#!/usr/bin/env python3
"""
JARVIS Text Mode - Interactive text-based interface
Perfect for when microphone is not available
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import JARVIS without voice
from conversational_jarvis import ConversationalJARVIS


def print_banner():
    """Print JARVIS banner."""
    print("\n╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  JARVIS - Text Mode".center(68) + "║")
    print("║" + "  Type Your Commands - All Features Available".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝\n")


def print_help():
    """Print available commands."""
    print("\n💡 Example Commands:\n")
    print("  🎵 Music:")
    print("     'Play Despacito'")
    print("     'Volume up'")
    print("     'Set volume to 50'")
    print()
    print("  ⌨️  Computer Control:")
    print("     'Type hello world'")
    print("     'Press Enter'")
    print("     'Search for document'")
    print()
    print("  🪟 Windows:")
    print("     'Switch window'")
    print("     'Close window'")
    print("     'Minimize'")
    print()
    print("  📁 Navigation:")
    print("     'Go to desktop'")
    print("     'Open Chrome'")
    print()
    print("  ℹ️  Information:")
    print("     'What time is it?'")
    print("     'Check my computer'")
    print()
    print("  Type 'help' for this list")
    print("  Type 'exit' or 'quit' to exit")
    print()


def main():
    """Run JARVIS in text mode."""
    print_banner()
    
    # Initialize JARVIS in text-only mode
    print("🔄 Initializing JARVIS...")
    jarvis = ConversationalJARVIS(voice_enabled=False)
    
    print("✅ JARVIS ready!\n")
    
    # Greeting
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    print(f"🗣️  JARVIS: {greeting}! I'm ready to help.")
    print("🗣️  JARVIS: Type your commands below. Type 'help' for examples.\n")
    
    # Main loop
    while jarvis.listening:
        try:
            # Get user input
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Check for special commands
            if user_input.lower() in ['help', '?']:
                print_help()
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("\n🗣️  JARVIS: Goodbye! I'll be here if you need me.\n")
                break
            
            # Process command
            print()  # Blank line for readability
            jarvis.handle_conversation(user_input.lower())
            print()  # Blank line after response
            
        except KeyboardInterrupt:
            print("\n\n🗣️  JARVIS: Goodbye! I'll be here if you need me.\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            continue


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("\nMake sure:")
        print("  - LLM_API_KEY is set in .env")
        print("  - All dependencies are installed")
        print("  - Internet connection is available")
        sys.exit(1)
