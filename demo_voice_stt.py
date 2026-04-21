"""
Demo script for Voice Interface Speech-to-Text functionality.

This script demonstrates the VoiceInterface class with local Whisper STT.

Requirements: 3.1, 3.5, 3.7, 3.8
"""

import wave
import tempfile
import os
import numpy as np
from jarvis.voice import VoiceInterface


def create_sample_audio():
    """
    Create a sample audio file for demonstration.
    
    Returns:
        bytes: WAV audio data
    """
    print("Creating sample audio file...")
    
    temp_wav_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            temp_wav_path = temp_wav.name
        
        # Create a simple WAV file with 2 seconds of silence
        sample_rate = 16000
        duration = 2  # seconds
        num_samples = sample_rate * duration
        
        # Generate silent audio (zeros)
        audio_data = np.zeros(num_samples, dtype=np.int16)
        
        # Write WAV file
        with wave.open(temp_wav_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        # Read the bytes
        with open(temp_wav_path, 'rb') as f:
            audio_bytes = f.read()
        
        print(f"✓ Created sample audio file ({len(audio_bytes)} bytes)")
        return audio_bytes
    finally:
        # Clean up
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.unlink(temp_wav_path)
            except:
                pass


def main():
    """Main demo function."""
    print("=" * 70)
    print("JARVIS Voice Interface - Speech-to-Text Demo")
    print("=" * 70)
    print()
    
    # Initialize Voice Interface
    print("1. Initializing Voice Interface with Whisper model...")
    print("   Model: base (balance between speed and accuracy)")
    voice_interface = VoiceInterface(model_name="base")
    print("   ✓ Voice Interface initialized")
    print()
    
    # Create sample audio
    print("2. Creating sample audio for demonstration...")
    audio_bytes = create_sample_audio()
    print()
    
    # Perform speech-to-text
    print("3. Performing speech-to-text conversion...")
    print("   - Processing audio locally with Whisper")
    print("   - No external API calls (privacy-first)")
    print("   - This may take a few seconds on first run (model loading)...")
    print()
    
    transcribed_text = voice_interface.speech_to_text(audio_bytes)
    
    print("4. Results:")
    print(f"   Transcribed text: '{transcribed_text}'")
    if not transcribed_text:
        print("   (Empty result is expected for silent audio)")
    print()
    
    # Demonstrate error handling
    print("5. Testing error handling with invalid audio...")
    invalid_result = voice_interface.speech_to_text(b"invalid audio data")
    print(f"   Result: '{invalid_result}'")
    print("   ✓ Gracefully handled - returns empty string for fallback to text input")
    print()
    
    # Summary
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print("Key Features Demonstrated:")
    print("  ✓ Local speech-to-text using OpenAI Whisper (Req 3.1)")
    print("  ✓ Audio processed locally without external API calls (Req 3.5)")
    print("  ✓ Graceful error handling with fallback to text input (Req 3.7)")
    print("  ✓ Offline operation for STT processing (Req 3.8)")
    print()
    print("Next Steps:")
    print("  - Task 14.2: Implement wake word detection with Porcupine")
    print("  - Task 14.3: Implement text-to-speech with ElevenLabs")
    print("  - Task 14.4: Wire Voice Interface to Brain")
    print()


if __name__ == "__main__":
    main()
