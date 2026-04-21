"""Demo script for testing ElevenLabs TTS functionality."""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jarvis.voice.voice_interface import VoiceInterface

def main():
    """Test the text-to-speech functionality."""
    # Load environment variables
    load_dotenv()
    
    # Get ElevenLabs API key from environment
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not elevenlabs_api_key or elevenlabs_api_key == "your_elevenlabs_api_key_here":
        print("ERROR: ELEVENLABS_API_KEY not set in .env file")
        print("Please set a valid ElevenLabs API key to test TTS functionality")
        return
    
    print("Initializing Voice Interface with ElevenLabs TTS...")
    voice_interface = VoiceInterface(
        model_name="base",
        elevenlabs_api_key=elevenlabs_api_key,
        voice_id="Rachel"  # Using Rachel voice
    )
    
    # Test text
    test_text = "Hello Boss! I am JARVIS, your personal AI assistant. Text-to-speech is now working perfectly."
    
    print(f"\nConverting text to speech: '{test_text}'")
    
    try:
        # Convert text to speech
        audio_bytes = voice_interface.text_to_speech(test_text)
        print(f"✓ Generated {len(audio_bytes)} bytes of audio")
        
        # Play the audio
        print("\nPlaying audio...")
        voice_interface.play_audio(audio_bytes)
        print("✓ Audio playback completed")
        
        print("\n✓ TTS test completed successfully!")
        
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
    except RuntimeError as e:
        print(f"\n✗ Runtime error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
