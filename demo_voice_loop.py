"""
Demo script for complete voice interaction loop.

This script demonstrates the full voice pipeline:
1. Listen for "Hey Jarvis" wake word
2. Record audio after wake word detection
3. Convert audio to text using STT
4. Process with Brain
5. Convert response to speech using TTS
6. Play audio response
7. Return to listening

Requirements:
- PORCUPINE_ACCESS_KEY environment variable must be set
- ELEVENLABS_API_KEY environment variable must be set
- ANTHROPIC_API_KEY environment variable must be set
- Microphone and speakers must be available

Run with: python demo_voice_loop.py
"""

import os
import sys
from dotenv import load_dotenv

from jarvis.voice import VoiceInterface
from jarvis.brain import Brain
from jarvis.config import Configuration

# Load environment variables
load_dotenv()


def text_fallback_handler(error_msg: str) -> str:
    """
    Handle voice failure by falling back to text input.
    
    Args:
        error_msg: Error message describing the failure
        
    Returns:
        User's text input
    """
    print(f"\n⚠️  {error_msg}")
    print("Falling back to text input...\n")
    return input("You: ")


def main():
    """Main demo function."""
    print("=" * 70)
    print("JARVIS Voice Interaction Loop Demo")
    print("=" * 70)
    print()
    
    # Check required environment variables
    porcupine_key = os.getenv("PORCUPINE_ACCESS_KEY")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    missing_keys = []
    if not porcupine_key or porcupine_key == "your_porcupine_access_key_here":
        missing_keys.append("PORCUPINE_ACCESS_KEY")
    if not elevenlabs_key or elevenlabs_key == "your_elevenlabs_api_key_here":
        missing_keys.append("ELEVENLABS_API_KEY")
    if not anthropic_key or anthropic_key == "your_anthropic_api_key_here":
        missing_keys.append("ANTHROPIC_API_KEY")
    
    if missing_keys:
        print("❌ Error: Missing required environment variables:")
        for key in missing_keys:
            print(f"   - {key}")
        print()
        print("Please configure these in your .env file.")
        print()
        sys.exit(1)
    
    print("✅ All required API keys found")
    print()
    
    # Initialize configuration
    print("Initializing JARVIS components...")
    config = Configuration(
        llm_api_key=anthropic_key,
        llm_model="claude-sonnet-4-20250514"
    )
    
    # Initialize Brain
    brain = Brain(config)
    print("✅ Brain initialized")
    
    # Initialize Voice Interface
    voice_interface = VoiceInterface(
        model_name="base",  # Use base model for good accuracy
        porcupine_access_key=porcupine_key,
        elevenlabs_api_key=elevenlabs_key,
        voice_id="Rachel"
    )
    print("✅ Voice Interface initialized")
    print()
    
    # Display instructions
    print("-" * 70)
    print("Voice Interaction Loop Ready!")
    print("-" * 70)
    print()
    print("How to use:")
    print("  1. Say 'Jarvis' to activate the assistant")
    print("  2. After the wake word is detected, speak your command")
    print("  3. JARVIS will process your request and respond with voice")
    print("  4. The loop continues until you press Ctrl+C")
    print()
    print("Features:")
    print("  ✓ Wake word detection (Porcupine)")
    print("  ✓ Local speech-to-text (Whisper)")
    print("  ✓ LLM reasoning (Claude)")
    print("  ✓ Natural text-to-speech (ElevenLabs)")
    print("  ✓ Automatic fallback to text input on voice failure")
    print()
    print("Press Ctrl+C to stop")
    print("-" * 70)
    print()
    
    try:
        # Start voice interaction loop
        voice_interface.voice_interaction_loop(
            brain=brain,
            session_id="demo_session",
            memory_context="",
            on_text_fallback=text_fallback_handler,
            recording_duration=5.0  # Record for 5 seconds after wake word
        )
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping voice interaction loop...")
        print("✅ Demo completed successfully!")
        print()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
