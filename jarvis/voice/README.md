# JARVIS Voice Interface

This module provides speech-to-text (STT) and text-to-speech (TTS) capabilities for the JARVIS personal AI assistant.

## Features

### Implemented
- ✅ **Local Speech-to-Text** (Task 14.1): Uses OpenAI Whisper for privacy-first audio processing
- ✅ **Wake Word Detection** (Task 14.2): Porcupine integration for "Hey Jarvis"
- ✅ **Text-to-Speech** (Task 14.3): ElevenLabs API integration for natural voice output
- ✅ **Audio Playback** (Task 14.3): Speaker output using sounddevice
- ✅ **Error Handling**: Graceful fallback to text input on failures
- ✅ **Offline Operation**: No external API calls for STT
- ✅ **Multiple Model Sizes**: Support for tiny, base, small, medium, and large Whisper models
- ✅ **Background Wake Word Listening**: Continuous detection in separate thread

### Coming Soon
- ⏳ **Voice Pipeline** (Task 14.4): Complete wake word → STT → Brain → TTS flow

## Requirements

### System Dependencies

**FFmpeg** is required for Whisper to process audio files:

- **Windows**: 
  1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
  2. Extract and add to PATH
  3. Or use: `choco install ffmpeg` (with Chocolatey)

- **Linux**: 
  ```bash
  sudo apt-get install ffmpeg
  ```

- **macOS**: 
  ```bash
  brew install ffmpeg
  ```

### Python Dependencies

All Python dependencies are listed in `requirements.txt`:
- `openai-whisper==20231117` - Local speech-to-text
- `elevenlabs==1.9.0` - Text-to-speech API
- `pvporcupine==3.0.3` - Wake word detection
- `numpy==2.2.1` - Audio processing
- `sounddevice==0.5.1` - Audio I/O
- `soundfile==0.12.1` - Audio file reading for playback

## Usage

### Basic Speech-to-Text

```python
from jarvis.voice import VoiceInterface

# Initialize with default 'base' model
voice_interface = VoiceInterface()

# Or specify a different model for speed/accuracy tradeoff
voice_interface = VoiceInterface(model_name="tiny")  # Faster
voice_interface = VoiceInterface(model_name="small")  # Balanced
voice_interface = VoiceInterface(model_name="large")  # Most accurate

# Convert audio bytes to text
audio_bytes = load_audio_file("recording.wav")
transcribed_text = voice_interface.speech_to_text(audio_bytes)

if transcribed_text:
    print(f"Transcribed: {transcribed_text}")
else:
    print("Transcription failed, falling back to text input")
```

### Wake Word Detection

```python
from jarvis.voice import VoiceInterface
import os

# Get Porcupine access key from environment
porcupine_key = os.getenv("PORCUPINE_ACCESS_KEY")

# Initialize with Porcupine access key
voice_interface = VoiceInterface(
    model_name="base",
    porcupine_access_key=porcupine_key
)

# Define callback for when wake word is detected
def on_wake_word():
    print("Wake word 'Jarvis' detected!")
    # Start listening for voice command
    # ... your code here ...

# Register the callback
voice_interface.on_wake_word_detected(on_wake_word)

# Start continuous wake word detection (runs in background thread)
voice_interface.start_wake_word_detection()

# Your application continues running...
# The callback will be invoked when "Jarvis" is detected

# When done, stop wake word detection
voice_interface.stop_wake_word_detection()
```

### Getting a Porcupine Access Key

1. Sign up for a free account at [Picovoice Console](https://console.picovoice.ai/)
2. Create a new access key in the console
3. Add it to your `.env` file:
   ```bash
   PORCUPINE_ACCESS_KEY=your_access_key_here
   ```

The free tier includes:
- Unlimited wake word detections
- Built-in keywords including "Jarvis"
- No credit card required

### Text-to-Speech

```python
from jarvis.voice import VoiceInterface
import os

# Get ElevenLabs API key from environment
elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")

# Initialize with ElevenLabs API key
voice_interface = VoiceInterface(
    model_name="base",
    elevenlabs_api_key=elevenlabs_key,
    voice_id="Rachel"  # Default voice
)

# Convert text to speech
text = "Hello Boss! I am JARVIS, your personal AI assistant."
audio_bytes = voice_interface.text_to_speech(text)

# Play the audio through speakers
voice_interface.play_audio(audio_bytes)
```

### Getting an ElevenLabs API Key

1. Sign up for an account at [ElevenLabs](https://elevenlabs.io/)
2. Navigate to your profile settings
3. Copy your API key
4. Add it to your `.env` file:
   ```bash
   ELEVENLABS_API_KEY=your_api_key_here
   ```

The free tier includes:
- 10,000 characters per month
- Access to all voices
- High-quality audio output

### Available Voices

ElevenLabs provides several pre-made voices:
- **Rachel** (default) - Clear, professional female voice
- **Adam** - Warm, friendly male voice
- **Antoni** - Deep, authoritative male voice
- **Arnold** - Strong, confident male voice
- **Bella** - Soft, gentle female voice
- **Domi** - Energetic, youthful female voice
- **Elli** - Calm, soothing female voice
- **Josh** - Casual, conversational male voice
- **Sam** - Neutral, versatile male voice

You can also create custom voices in the ElevenLabs dashboard.

### Model Selection

Choose the Whisper model based on your needs:

| Model  | Size  | Speed      | Accuracy | Use Case                    |
|--------|-------|------------|----------|-----------------------------|
| tiny   | 39M   | Very Fast  | Good     | Testing, low-power devices  |
| base   | 74M   | Fast       | Better   | **Default**, balanced       |
| small  | 244M  | Moderate   | Good     | Better accuracy needed      |
| medium | 769M  | Slow       | Better   | High accuracy required      |
| large  | 1550M | Very Slow  | Best     | Maximum accuracy            |

### Error Handling

The `speech_to_text()` method is designed to fail gracefully:

```python
# Returns empty string on any error
result = voice_interface.speech_to_text(invalid_audio)
if not result:
    # Fall back to text input
    user_input = input("Voice failed. Please type your message: ")
```

## Architecture

### Privacy-First Design

All speech-to-text processing happens **locally** on your machine:
- ✅ Audio never leaves your device
- ✅ No external API calls for STT
- ✅ No cloud dependencies
- ✅ Works completely offline

### Requirements Mapping

This implementation satisfies the following requirements:

- **Requirement 3.1**: Uses OpenAI Whisper running locally for STT conversion
- **Requirement 3.2**: Uses ElevenLabs API for TTS conversion
- **Requirement 3.3**: Detects "Hey Jarvis" wake word and activates listening mode
- **Requirement 3.4**: Uses Porcupine for wake word detection
- **Requirement 3.5**: Processes audio locally without sending to external services
- **Requirement 3.6**: Converts Brain responses to natural speech output and plays to speakers
- **Requirement 3.7**: Falls back to text input on voice failure
- **Requirement 3.8**: Operates offline for STT processing

## Testing

### Unit Tests

Run unit tests with mocked Whisper model:

```bash
pytest tests/unit/test_voice_interface.py -v
```

### Integration Tests

Run integration tests with real Whisper model:

```bash
pytest tests/integration/test_voice_interface_integration.py -v -m integration
```

### Demo Script

Try the demo scripts to see the voice interface in action:

```bash
# Test speech-to-text
python demo_voice_stt.py

# Test wake word detection
python demo_wake_word.py

# Test text-to-speech (requires ELEVENLABS_API_KEY)
python demo_tts.py
```

## Performance

### First Run
- Model download: ~140MB (one-time)
- Model loading: 2-5 seconds
- Transcription: 1-3 seconds per audio clip

### Subsequent Runs
- Model loading: Cached (instant)
- Transcription: 1-3 seconds per audio clip

### Optimization Tips

1. **Use smaller models** for faster processing:
   ```python
   voice_interface = VoiceInterface(model_name="tiny")
   ```

2. **Keep the model loaded** between transcriptions (automatic caching)

3. **Process shorter audio clips** for faster results

## Troubleshooting

### "ffmpeg not found" Error

**Problem**: Whisper requires ffmpeg to process audio files.

**Solution**: Install ffmpeg (see System Dependencies above)

### "ElevenLabs API key is required" Error

**Problem**: Text-to-speech requires an ElevenLabs API key.

**Solution**: 
1. Get an API key from [ElevenLabs](https://elevenlabs.io/)
2. Add it to your `.env` file: `ELEVENLABS_API_KEY=your_key_here`
3. Pass it when initializing: `VoiceInterface(elevenlabs_api_key=key)`

### "Porcupine access key is required" Error

**Problem**: Wake word detection requires a Porcupine access key.

**Solution**: 
1. Get a free access key from [Picovoice Console](https://console.picovoice.ai/)
2. Add it to your `.env` file: `PORCUPINE_ACCESS_KEY=your_key_here`
3. Pass it when initializing: `VoiceInterface(porcupine_access_key=key)`

### Audio Playback Fails

**Problem**: `play_audio()` raises an error.

**Possible Causes**:
- No audio output device available
- Audio device is in use by another application
- Invalid audio format
- soundfile library not installed

**Solutions**:
- Ensure speakers/headphones are connected
- Close other applications using audio
- Install soundfile: `pip install soundfile`
- Check audio device: `python -c "import sounddevice as sd; print(sd.query_devices())"`

### TTS API Errors

**Problem**: Text-to-speech fails with API error.

**Possible Causes**:
- Invalid API key
- API quota exceeded
- Network connectivity issues
- ElevenLabs service outage

**Solutions**:
- Verify API key is correct
- Check your ElevenLabs account quota
- Test network connectivity
- Check [ElevenLabs status page](https://status.elevenlabs.io/)

### Wake Word Not Detected

**Problem**: Wake word detection is running but not detecting "Jarvis".

**Possible Causes**:
- Microphone not working or not accessible
- Background noise too loud
- Speaking too quietly or unclearly
- Wrong microphone selected

**Debug**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Check if audio stream is working
import sounddevice as sd
print(sd.query_devices())  # List available audio devices
```

### Slow Transcription

**Problem**: Transcription takes too long.

**Solutions**:
- Use a smaller model (`tiny` or `base`)
- Process shorter audio clips
- Ensure you have adequate CPU/GPU resources

### Empty Transcription Results

**Problem**: `speech_to_text()` returns empty string.

**Possible Causes**:
- Silent or very quiet audio
- Invalid audio format
- Audio file corruption
- ffmpeg not installed

**Debug**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run your code - check logs for detailed error messages
```

## Next Steps

### Task 14.4: Complete Voice Pipeline
- Wire wake word → STT → Brain → TTS
- Implement voice interaction loop
- Add comprehensive error handling and fallbacks
- Create end-to-end voice interaction demo

## Contributing

When adding new features to the voice interface:

1. Follow the existing error handling patterns
2. Maintain privacy-first design (local processing)
3. Add comprehensive unit and integration tests
4. Update this README with new functionality
5. Ensure backward compatibility

## License

Part of the JARVIS Personal AI Assistant project.
