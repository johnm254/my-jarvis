"""
Demo script for wake word detection with Porcupine.

This script demonstrates the wake word detection functionality of the JARVIS voice interface.
It listens continuously for the wake word "Jarvis" and triggers a callback when detected.

Requirements:
- PORCUPINE_ACCESS_KEY environment variable must be set
- Microphone must be available and accessible
- Run with: python demo_wake_word.py

To get a Porcupine access key:
1. Sign up at https://console.picovoice.ai/
2. Create a new access key (free tier available)
3. Add to .env file: PORCUPINE_ACCESS_KEY=your_key_here
"""

import os
import sys
import time
from dotenv import load_dotenv

from jarvis.voice import VoiceInterface

# Load environment variables
load_dotenv()


def on_wake_word_detected():
    """Callback function invoked when wake word is detected."""
    print("\n🎤 Wake word 'Jarvis' detected!")
    print("   (In a real application, this would start listening for a voice command)")
    print("   Listening for next wake word...\n")


def main():
    """Main demo function."""
    print("=" * 70)
    print("JARVIS Wake Word Detection Demo")
    print("=" * 70)
    print()
    
    # Get Porcupine access key
    porcupine_key = os.getenv("PORCUPINE_ACCESS_KEY")
    
    if not porcupine_key or porcupine_key == "your_porcupine_access_key_here":
        print("❌ Error: PORCUPINE_ACCESS_KEY not configured")
        print()
        print("To get a Porcupine access key:")
        print("1. Sign up at https://console.picovoice.ai/")
        print("2. Create a new access key (free tier available)")
        print("3. Add to .env file: PORCUPINE_ACCESS_KEY=your_key_here")
        print()
        sys.exit(1)
    
    print("✅ Porcupine access key found")
    print()
    
    # Initialize voice interface
    print("Initializing voice interface...")
    voice_interface = VoiceInterface(
        model_name="tiny",  # Use tiny model for faster demo
        porcupine_access_key=porcupine_key
    )
    print("✅ Voice interface initialized")
    print()
    
    # Register wake word callback
    voice_interface.on_wake_word_detected(on_wake_word_detected)
    print("✅ Wake word callback registered")
    print()
    
    try:
        # Start wake word detection
        print("Starting wake word detection...")
        voice_interface.start_wake_word_detection()
        print("✅ Wake word detection started")
        print()
        
        print("-" * 70)
        print("🎧 Listening for wake word 'Jarvis'...")
        print("   Say 'Jarvis' to trigger the wake word detection")
        print("   Press Ctrl+C to stop")
        print("-" * 70)
        print()
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping wake word detection...")
        voice_interface.stop_wake_word_detection()
        print("✅ Wake word detection stopped")
        print()
        print("Demo completed successfully!")
        print()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print()
        voice_interface.stop_wake_word_detection()
        sys.exit(1)


if __name__ == "__main__":
    main()
