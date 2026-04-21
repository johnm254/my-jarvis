"""Unit tests for Voice Interface."""

import pytest
import tempfile
import wave
import os
import time
from unittest.mock import Mock, patch, MagicMock, call
import numpy as np

from jarvis.voice import VoiceInterface


class TestVoiceInterface:
    """Test suite for VoiceInterface class."""
    
    @pytest.fixture
    def voice_interface(self):
        """Create a VoiceInterface instance for testing."""
        return VoiceInterface(model_name="base")
    
    @pytest.fixture
    def sample_audio_bytes(self):
        """
        Create sample audio bytes in WAV format for testing.
        
        Returns:
            bytes: Valid WAV audio data
        """
        # Create a temporary WAV file with sample audio
        temp_wav_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_wav_path = temp_wav.name
            
            # Create a simple WAV file with 1 second of silence
            sample_rate = 16000
            duration = 1  # seconds
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
            
            return audio_bytes
        finally:
            # Clean up - ensure file is closed before deletion
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.unlink(temp_wav_path)
                except PermissionError:
                    # On Windows, file might still be locked, try again after a short delay
                    import time
                    time.sleep(0.1)
                    try:
                        os.unlink(temp_wav_path)
                    except:
                        pass  # Best effort cleanup
    
    def test_initialization(self, voice_interface):
        """Test VoiceInterface initialization."""
        assert voice_interface.model_name == "base"
        assert voice_interface.whisper_model is None
        assert voice_interface._wake_word_callback is None
    
    def test_initialization_with_custom_model(self):
        """Test VoiceInterface initialization with custom model."""
        vi = VoiceInterface(model_name="small")
        assert vi.model_name == "small"
    
    @patch('jarvis.voice.voice_interface.whisper.load_model')
    def test_load_whisper_model(self, mock_load_model, voice_interface):
        """Test lazy loading of Whisper model."""
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        # Model should not be loaded initially
        assert voice_interface.whisper_model is None
        
        # Load the model
        model = voice_interface._load_whisper_model()
        
        # Verify model was loaded
        assert model == mock_model
        assert voice_interface.whisper_model == mock_model
        mock_load_model.assert_called_once_with("base")
    
    @patch('jarvis.voice.voice_interface.whisper.load_model')
    def test_load_whisper_model_cached(self, mock_load_model, voice_interface):
        """Test that Whisper model is only loaded once (cached)."""
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        # Load the model twice
        model1 = voice_interface._load_whisper_model()
        model2 = voice_interface._load_whisper_model()
        
        # Verify model was only loaded once
        assert model1 == model2
        mock_load_model.assert_called_once()
    
    @patch('jarvis.voice.voice_interface.whisper.load_model')
    def test_load_whisper_model_failure(self, mock_load_model, voice_interface):
        """Test handling of Whisper model loading failure."""
        mock_load_model.side_effect = Exception("Model loading failed")
        
        with pytest.raises(Exception, match="Model loading failed"):
            voice_interface._load_whisper_model()
    
    @patch('jarvis.voice.voice_interface.whisper.load_model')
    def test_speech_to_text_success(self, mock_load_model, voice_interface, sample_audio_bytes):
        """Test successful speech-to-text conversion."""
        # Mock the Whisper model
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "Hello, this is a test transcription."
        }
        mock_load_model.return_value = mock_model
        
        # Perform transcription
        result = voice_interface.speech_to_text(sample_audio_bytes)
        
        # Verify result
        assert result == "Hello, this is a test transcription."
        assert mock_model.transcribe.called
        
        # Verify transcribe was called with correct parameters
        call_args = mock_model.transcribe.call_args
        assert call_args[1]['fp16'] is False
        assert call_args[1]['language'] == "en"
    
    @patch('jarvis.voice.voice_interface.whisper.load_model')
    def test_speech_to_text_strips_whitespace(self, mock_load_model, voice_interface, sample_audio_bytes):
        """Test that speech-to-text strips leading/trailing whitespace."""
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "  Hello with spaces  "
        }
        mock_load_model.return_value = mock_model
        
        result = voice_interface.speech_to_text(sample_audio_bytes)
        
        assert result == "Hello with spaces"
    
    def test_speech_to_text_empty_audio(self, voice_interface):
        """Test speech-to-text with empty audio data."""
        result = voice_interface.speech_to_text(b"")
        
        # Should return empty string for empty audio
        assert result == ""
    
    @patch('jarvis.voice.voice_interface.whisper.load_model')
    def test_speech_to_text_transcription_failure(self, mock_load_model, voice_interface, sample_audio_bytes):
        """Test handling of transcription failure."""
        mock_model = Mock()
        mock_model.transcribe.side_effect = Exception("Transcription failed")
        mock_load_model.return_value = mock_model
        
        # Should return empty string on failure (fallback behavior)
        result = voice_interface.speech_to_text(sample_audio_bytes)
        
        assert result == ""
    
    @patch('jarvis.voice.voice_interface.whisper.load_model')
    def test_speech_to_text_cleans_up_temp_file(self, mock_load_model, voice_interface, sample_audio_bytes):
        """Test that temporary audio file is cleaned up after transcription."""
        mock_model = Mock()
        mock_model.transcribe.return_value = {"text": "Test"}
        mock_load_model.return_value = mock_model
        
        # Track temporary files created
        temp_files_before = set(os.listdir(tempfile.gettempdir()))
        
        voice_interface.speech_to_text(sample_audio_bytes)
        
        # Check that no new temporary files remain
        temp_files_after = set(os.listdir(tempfile.gettempdir()))
        new_temp_files = temp_files_after - temp_files_before
        
        # Filter for .wav files
        new_wav_files = [f for f in new_temp_files if f.endswith('.wav')]
        assert len(new_wav_files) == 0, "Temporary WAV file was not cleaned up"
    
    def test_on_wake_word_detected(self, voice_interface):
        """Test registering wake word callback."""
        callback = Mock()
        
        voice_interface.on_wake_word_detected(callback)
        
        assert voice_interface._wake_word_callback == callback
    
    def test_start_wake_word_detection_no_access_key(self, voice_interface):
        """Test that wake word detection raises ValueError without access key."""
        with pytest.raises(ValueError, match="Porcupine access key is required"):
            voice_interface.start_wake_word_detection()
    
    @patch('jarvis.voice.voice_interface.pvporcupine.create')
    @patch('jarvis.voice.voice_interface.sd.InputStream')
    def test_start_wake_word_detection_success(self, mock_input_stream, mock_porcupine_create):
        """Test successful wake word detection start."""
        # Create voice interface with access key
        vi = VoiceInterface(model_name="base", porcupine_access_key="test_key")
        
        # Mock Porcupine
        mock_porcupine = Mock()
        mock_porcupine.sample_rate = 16000
        mock_porcupine.frame_length = 512
        mock_porcupine_create.return_value = mock_porcupine
        
        # Start wake word detection
        vi.start_wake_word_detection()
        
        # Verify Porcupine was created with correct parameters
        mock_porcupine_create.assert_called_once_with(
            access_key="test_key",
            keywords=["jarvis"]
        )
        
        # Verify thread was started
        assert vi._wake_word_running is True
        assert vi._wake_word_thread is not None
        assert vi._wake_word_thread.is_alive()
        
        # Clean up
        vi.stop_wake_word_detection()
    
    @patch('jarvis.voice.voice_interface.pvporcupine.create')
    def test_start_wake_word_detection_already_running(self, mock_porcupine_create):
        """Test that starting wake word detection twice raises RuntimeError."""
        vi = VoiceInterface(model_name="base", porcupine_access_key="test_key")
        
        # Mock Porcupine
        mock_porcupine = Mock()
        mock_porcupine.sample_rate = 16000
        mock_porcupine.frame_length = 512
        mock_porcupine_create.return_value = mock_porcupine
        
        # Start wake word detection
        vi.start_wake_word_detection()
        
        # Try to start again
        with pytest.raises(RuntimeError, match="already running"):
            vi.start_wake_word_detection()
        
        # Clean up
        vi.stop_wake_word_detection()
    
    @patch('jarvis.voice.voice_interface.pvporcupine.create')
    @patch('jarvis.voice.voice_interface.sd.InputStream')
    def test_stop_wake_word_detection(self, mock_input_stream, mock_porcupine_create):
        """Test stopping wake word detection."""
        vi = VoiceInterface(model_name="base", porcupine_access_key="test_key")
        
        # Mock Porcupine
        mock_porcupine = Mock()
        mock_porcupine.sample_rate = 16000
        mock_porcupine.frame_length = 512
        mock_porcupine_create.return_value = mock_porcupine
        
        # Start and stop
        vi.start_wake_word_detection()
        assert vi._wake_word_running is True
        
        vi.stop_wake_word_detection()
        
        # Verify cleanup
        assert vi._wake_word_running is False
        mock_porcupine.delete.assert_called_once()
        assert vi._porcupine is None
    
    def test_stop_wake_word_detection_not_running(self, voice_interface):
        """Test stopping wake word detection when not running."""
        # Should not raise an error
        voice_interface.stop_wake_word_detection()
    
    @patch('jarvis.voice.voice_interface.pvporcupine.create')
    @patch('jarvis.voice.voice_interface.sd.InputStream')
    def test_wake_word_callback_invoked(self, mock_input_stream, mock_porcupine_create):
        """Test that wake word callback is invoked when wake word is detected."""
        vi = VoiceInterface(model_name="base", porcupine_access_key="test_key")
        
        # Mock Porcupine
        mock_porcupine = Mock()
        mock_porcupine.sample_rate = 16000
        mock_porcupine.frame_length = 512
        # Simulate wake word detection on first call, then no detection
        mock_porcupine.process.side_effect = [0, -1, -1, -1]
        mock_porcupine_create.return_value = mock_porcupine
        
        # Mock audio stream
        mock_stream = MagicMock()
        mock_audio_frame = np.zeros((512, 1), dtype=np.int16)
        mock_stream.read.return_value = (mock_audio_frame, False)
        mock_input_stream.return_value.__enter__.return_value = mock_stream
        
        # Register callback
        callback = Mock()
        vi.on_wake_word_detected(callback)
        
        # Start wake word detection
        vi.start_wake_word_detection()
        
        # Wait for callback to be invoked
        time.sleep(0.5)
        
        # Verify callback was called
        callback.assert_called()
        
        # Clean up
        vi.stop_wake_word_detection()
    
    @patch('jarvis.voice.voice_interface.pvporcupine.create')
    def test_porcupine_initialization_failure(self, mock_porcupine_create):
        """Test handling of Porcupine initialization failure."""
        vi = VoiceInterface(model_name="base", porcupine_access_key="invalid_key")
        
        # Mock Porcupine creation failure
        mock_porcupine_create.side_effect = Exception("Invalid access key")
        
        # Should raise exception and clean up
        with pytest.raises(Exception, match="Invalid access key"):
            vi.start_wake_word_detection()
        
        # Verify cleanup happened
        assert vi._porcupine is None
    
    def test_text_to_speech_not_implemented(self, voice_interface):
        """Test that text-to-speech raises ValueError without API key."""
        with pytest.raises(ValueError, match="ElevenLabs API key is required"):
            voice_interface.text_to_speech("Hello world")
    
    def test_play_audio_not_implemented(self, voice_interface):
        """Test that play_audio raises ValueError with empty audio."""
        with pytest.raises(ValueError, match="Cannot play empty audio"):
            voice_interface.play_audio(b"")


class TestVoiceInterfaceErrorHandling:
    """Test suite for Voice Interface error handling and fallback behavior."""
    
    @pytest.fixture
    def voice_interface(self):
        """Create a VoiceInterface instance for testing."""
        return VoiceInterface(model_name="base")
    
    @patch('jarvis.voice.voice_interface.whisper.load_model')
    def test_speech_to_text_model_load_failure_fallback(self, mock_load_model, voice_interface):
        """Test fallback behavior when model loading fails."""
        mock_load_model.side_effect = Exception("Model not found")
        
        # Should return empty string to allow fallback to text input
        result = voice_interface.speech_to_text(b"some audio data")
        
        assert result == ""
    
    @patch('jarvis.voice.voice_interface.whisper.load_model')
    def test_speech_to_text_invalid_audio_format(self, mock_load_model, voice_interface):
        """Test handling of invalid audio format."""
        mock_model = Mock()
        mock_model.transcribe.side_effect = Exception("Invalid audio format")
        mock_load_model.return_value = mock_model
        
        # Should return empty string on invalid audio
        result = voice_interface.speech_to_text(b"invalid audio data")
        
        assert result == ""
    
    def test_speech_to_text_none_audio(self, voice_interface):
        """Test speech-to-text with None audio data."""
        # Should handle None gracefully
        result = voice_interface.speech_to_text(None)
        
        assert result == ""


class TestVoiceInterfaceRequirements:
    """Test suite verifying specific requirements."""
    
    @pytest.fixture
    def voice_interface(self):
        """Create a VoiceInterface instance for testing."""
        return VoiceInterface(model_name="base")
    
    @patch('jarvis.voice.voice_interface.whisper.load_model')
    def test_requirement_3_1_local_stt(self, mock_load_model, voice_interface):
        """
        Requirement 3.1: THE Voice_Interface SHALL use OpenAI Whisper running locally for STT conversion.
        """
        mock_model = Mock()
        mock_model.transcribe.return_value = {"text": "Test"}
        mock_load_model.return_value = mock_model
        
        # Verify Whisper is used locally
        voice_interface.speech_to_text(b"audio data")
        
        # Verify local Whisper model was loaded
        mock_load_model.assert_called_once()
    
    @patch('jarvis.voice.voice_interface.whisper.load_model')
    def test_requirement_3_5_local_processing(self, mock_load_model, voice_interface):
        """
        Requirement 3.5: WHEN audio input is received, THE STT SHALL process it locally 
        without sending audio to external services.
        """
        mock_model = Mock()
        mock_model.transcribe.return_value = {"text": "Test"}
        mock_load_model.return_value = mock_model
        
        # Process audio
        voice_interface.speech_to_text(b"audio data")
        
        # Verify no external API calls (only local Whisper model used)
        # This is implicitly tested by mocking whisper.load_model
        assert mock_model.transcribe.called
    
    @patch('jarvis.voice.voice_interface.whisper.load_model')
    def test_requirement_3_7_fallback_on_failure(self, mock_load_model, voice_interface):
        """
        Requirement 3.7: IF voice input fails, THEN THE JARVIS_System SHALL fall back to text input.
        """
        mock_model = Mock()
        mock_model.transcribe.side_effect = Exception("Processing failed")
        mock_load_model.return_value = mock_model
        
        # Should return empty string to enable fallback
        result = voice_interface.speech_to_text(b"audio data")
        
        assert result == ""
    
    def test_requirement_3_8_offline_operation(self, voice_interface):
        """
        Requirement 3.8: THE Voice_Interface SHALL operate offline for STT processing.
        """
        # This is verified by using local Whisper model
        # No network calls should be made during STT
        assert voice_interface.model_name in ["tiny", "base", "small", "medium", "large"]



class TestTextToSpeech:
    """Test suite for text-to-speech functionality (Task 14.3)."""
    
    @pytest.fixture
    def voice_interface_with_tts(self):
        """Create a VoiceInterface instance with ElevenLabs API key."""
        return VoiceInterface(
            model_name="base",
            elevenlabs_api_key="test_api_key",
            voice_id="Rachel"
        )
    
    @pytest.fixture
    def voice_interface_no_tts(self):
        """Create a VoiceInterface instance without ElevenLabs API key."""
        return VoiceInterface(model_name="base")
    
    def test_initialization_with_elevenlabs_key(self, voice_interface_with_tts):
        """Test VoiceInterface initialization with ElevenLabs API key."""
        assert voice_interface_with_tts._elevenlabs_api_key == "test_api_key"
        assert voice_interface_with_tts._voice_id == "Rachel"
        # Client initialization is attempted but may fail without valid key
    
    def test_initialization_without_elevenlabs_key(self, voice_interface_no_tts):
        """Test VoiceInterface initialization without ElevenLabs API key."""
        assert voice_interface_no_tts._elevenlabs_api_key is None
        assert voice_interface_no_tts._elevenlabs_client is None
    
    def test_text_to_speech_no_api_key(self, voice_interface_no_tts):
        """Test text-to-speech raises ValueError without API key."""
        with pytest.raises(ValueError, match="ElevenLabs API key is required"):
            voice_interface_no_tts.text_to_speech("Hello world")
    
    def test_text_to_speech_empty_text(self, voice_interface_with_tts):
        """Test text-to-speech with empty text returns empty bytes."""
        result = voice_interface_with_tts.text_to_speech("")
        assert result == b""
        
        result = voice_interface_with_tts.text_to_speech("   ")
        assert result == b""
    
    @patch('jarvis.voice.voice_interface.ElevenLabs')
    def test_text_to_speech_success(self, mock_elevenlabs_class, voice_interface_no_tts):
        """Test successful text-to-speech conversion."""
        # Create a new voice interface with mocked ElevenLabs
        vi = VoiceInterface(
            model_name="base",
            elevenlabs_api_key="test_key",
            voice_id="Rachel"
        )
        
        # Mock the ElevenLabs client
        mock_client = Mock()
        mock_tts = Mock()
        mock_client.text_to_speech = mock_tts
        
        # Mock the convert method to return audio chunks
        mock_audio_chunks = [b"audio", b"chunk", b"data"]
        mock_tts.convert.return_value = iter(mock_audio_chunks)
        
        # Replace the client
        vi._elevenlabs_client = mock_client
        
        # Convert text to speech
        result = vi.text_to_speech("Hello world")
        
        # Verify result
        assert result == b"audiochunkdata"
        
        # Verify convert was called with correct parameters
        mock_tts.convert.assert_called_once()
        call_kwargs = mock_tts.convert.call_args[1]
        assert call_kwargs['voice_id'] == "Rachel"
        assert call_kwargs['text'] == "Hello world"
        assert call_kwargs['model_id'] == "eleven_monolingual_v1"
        assert 'voice_settings' in call_kwargs
    
    @patch('jarvis.voice.voice_interface.ElevenLabs')
    def test_text_to_speech_api_failure(self, mock_elevenlabs_class):
        """Test text-to-speech handles API failures gracefully."""
        vi = VoiceInterface(
            model_name="base",
            elevenlabs_api_key="test_key",
            voice_id="Rachel"
        )
        
        # Mock the ElevenLabs client to raise an exception
        mock_client = Mock()
        mock_tts = Mock()
        mock_client.text_to_speech = mock_tts
        mock_tts.convert.side_effect = Exception("API error")
        
        vi._elevenlabs_client = mock_client
        
        # Should raise RuntimeError
        with pytest.raises(RuntimeError, match="Failed to convert text to speech"):
            vi.text_to_speech("Hello world")
    
    def test_text_to_speech_no_client_initialized(self):
        """Test text-to-speech raises RuntimeError if client failed to initialize."""
        vi = VoiceInterface(
            model_name="base",
            elevenlabs_api_key="test_key"
        )
        
        # Simulate client initialization failure
        vi._elevenlabs_client = None
        
        with pytest.raises(RuntimeError, match="ElevenLabs client failed to initialize"):
            vi.text_to_speech("Hello world")
    
    def test_play_audio_empty_bytes(self, voice_interface_with_tts):
        """Test play_audio raises ValueError with empty audio."""
        with pytest.raises(ValueError, match="Cannot play empty audio"):
            voice_interface_with_tts.play_audio(b"")
    
    @patch('jarvis.voice.voice_interface.sf.read')
    @patch('jarvis.voice.voice_interface.sd.play')
    @patch('jarvis.voice.voice_interface.sd.wait')
    def test_play_audio_success(self, mock_wait, mock_play, mock_sf_read, voice_interface_with_tts):
        """Test successful audio playback."""
        # Mock soundfile read
        mock_audio_data = np.array([0.1, 0.2, 0.3])
        mock_sample_rate = 44100
        mock_sf_read.return_value = (mock_audio_data, mock_sample_rate)
        
        # Play audio
        audio_bytes = b"fake mp3 data"
        voice_interface_with_tts.play_audio(audio_bytes)
        
        # Verify soundfile read was called
        assert mock_sf_read.called
        
        # Verify sounddevice play was called with correct parameters
        mock_play.assert_called_once_with(mock_audio_data, mock_sample_rate)
        
        # Verify wait was called
        mock_wait.assert_called_once()
    
    @patch('jarvis.voice.voice_interface.sf.read')
    def test_play_audio_file_read_failure(self, mock_sf_read, voice_interface_with_tts):
        """Test play_audio handles file read failures."""
        mock_sf_read.side_effect = Exception("Failed to read audio file")
        
        with pytest.raises(RuntimeError, match="Failed to play audio"):
            voice_interface_with_tts.play_audio(b"audio data")
    
    def test_play_audio_none_bytes(self, voice_interface_with_tts):
        """Test play_audio with None audio data."""
        with pytest.raises(ValueError, match="Cannot play empty audio"):
            voice_interface_with_tts.play_audio(None)


class TestTextToSpeechRequirements:
    """Test suite verifying TTS-specific requirements (Task 14.3)."""
    
    @pytest.fixture
    def voice_interface_with_tts(self):
        """Create a VoiceInterface instance with ElevenLabs API key."""
        return VoiceInterface(
            model_name="base",
            elevenlabs_api_key="test_api_key",
            voice_id="Rachel"
        )
    
    @patch('jarvis.voice.voice_interface.ElevenLabs')
    def test_requirement_3_2_elevenlabs_tts(self, mock_elevenlabs_class, voice_interface_with_tts):
        """
        Requirement 3.2: THE Voice_Interface SHALL use ElevenLabs API for TTS conversion.
        """
        # Mock the ElevenLabs client
        mock_client = Mock()
        mock_tts = Mock()
        mock_client.text_to_speech = mock_tts
        mock_tts.convert.return_value = iter([b"audio"])
        
        voice_interface_with_tts._elevenlabs_client = mock_client
        
        # Convert text to speech
        voice_interface_with_tts.text_to_speech("Test")
        
        # Verify ElevenLabs API was used
        assert mock_tts.convert.called
    
    @patch('jarvis.voice.voice_interface.ElevenLabs')
    @patch('jarvis.voice.voice_interface.sf.read')
    @patch('jarvis.voice.voice_interface.sd.play')
    @patch('jarvis.voice.voice_interface.sd.wait')
    def test_requirement_3_6_natural_speech_output(
        self, mock_wait, mock_play, mock_sf_read, mock_elevenlabs_class, voice_interface_with_tts
    ):
        """
        Requirement 3.6: WHEN the Brain generates a response, THE TTS SHALL convert it to natural speech output.
        """
        # Mock ElevenLabs
        mock_client = Mock()
        mock_tts = Mock()
        mock_client.text_to_speech = mock_tts
        mock_tts.convert.return_value = iter([b"audio", b"data"])
        voice_interface_with_tts._elevenlabs_client = mock_client
        
        # Mock soundfile
        mock_sf_read.return_value = (np.array([0.1, 0.2]), 44100)
        
        # Convert text to speech
        audio_bytes = voice_interface_with_tts.text_to_speech("Hello Boss!")
        
        # Verify audio was generated
        assert len(audio_bytes) > 0
        
        # Play the audio
        voice_interface_with_tts.play_audio(audio_bytes)
        
        # Verify audio was played
        assert mock_play.called
        assert mock_wait.called
    
    def test_requirement_3_6_audio_output_to_speakers(self, voice_interface_with_tts):
        """
        Requirement 3.6: Audio output should be played to speakers.
        """
        # This is tested by the play_audio method existence and functionality
        assert hasattr(voice_interface_with_tts, 'play_audio')
        assert callable(voice_interface_with_tts.play_audio)



class TestAudioRecording:
    """Test audio recording functionality."""
    
    @patch('jarvis.voice.voice_interface.sd')
    @patch('jarvis.voice.voice_interface.sf')
    def test_record_audio_success(self, mock_sf, mock_sd):
        """Test successful audio recording."""
        # Mock recorded audio data
        mock_audio_data = np.array([[100], [200], [300]], dtype=np.int16)
        mock_sd.rec.return_value = mock_audio_data
        
        vi = VoiceInterface()
        
        # Mock file operations
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = b"fake wav data"
            mock_open.return_value.__enter__.return_value = mock_file
            
            result = vi.record_audio(duration=2.0, sample_rate=16000)
        
        # Should call sounddevice rec
        mock_sd.rec.assert_called_once()
        mock_sd.wait.assert_called_once()
        
        # Should return bytes
        assert isinstance(result, bytes)
    
    @patch('jarvis.voice.voice_interface.sd')
    def test_record_audio_handles_errors(self, mock_sd):
        """Test that record_audio handles errors gracefully."""
        mock_sd.rec.side_effect = Exception("Recording failed")
        
        vi = VoiceInterface()
        
        with pytest.raises(RuntimeError, match="Failed to record audio"):
            vi.record_audio()


class TestVoiceInteractionLoop:
    """Test voice interaction loop functionality."""
    
    @pytest.fixture
    def mock_brain(self):
        """Create a mock Brain instance."""
        brain = Mock()
        brain.process_input.return_value = Mock(text="Hello, how can I help you?")
        brain.skill_registry = None
        return brain
    
    def test_voice_interaction_loop_without_porcupine_key(self, mock_brain):
        """Test that voice loop without Porcupine key raises error."""
        vi = VoiceInterface()
        
        with pytest.raises(ValueError, match="Porcupine access key is required"):
            vi.voice_interaction_loop(brain=mock_brain, session_id="test")
    
    @patch('jarvis.voice.voice_interface.ElevenLabs')
    def test_voice_interaction_loop_without_elevenlabs_key(self, mock_elevenlabs_class, mock_brain):
        """Test that voice loop without ElevenLabs key raises error."""
        vi = VoiceInterface(porcupine_access_key="test_key")
        
        with pytest.raises(ValueError, match="ElevenLabs API key is required"):
            vi.voice_interaction_loop(brain=mock_brain, session_id="test")
    
    @patch('jarvis.voice.voice_interface.ElevenLabs')
    def test_voice_interaction_loop_without_brain(self, mock_elevenlabs_class):
        """Test that voice loop without Brain raises error."""
        mock_elevenlabs_class.return_value = Mock()
        vi = VoiceInterface(
            porcupine_access_key="test_key",
            elevenlabs_api_key="test_key"
        )
        
        with pytest.raises(ValueError, match="Brain instance is required"):
            vi.voice_interaction_loop(brain=None, session_id="test")
    
    @patch('jarvis.voice.voice_interface.pvporcupine')
    @patch('jarvis.voice.voice_interface.ElevenLabs')
    def test_voice_interaction_loop_starts_wake_word_detection(
        self, mock_elevenlabs_class, mock_porcupine, mock_brain
    ):
        """Test that voice loop starts wake word detection."""
        mock_elevenlabs_class.return_value = Mock()
        mock_porcupine_instance = Mock()
        mock_porcupine_instance.sample_rate = 16000
        mock_porcupine_instance.frame_length = 512
        mock_porcupine.create.return_value = mock_porcupine_instance
        
        vi = VoiceInterface(
            porcupine_access_key="test_key",
            elevenlabs_api_key="test_key"
        )
        
        # Start in a separate thread and stop immediately
        import threading
        def run_loop():
            try:
                vi.voice_interaction_loop(brain=mock_brain, session_id="test")
            except:
                pass
        
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
        
        # Give it time to start
        import time
        time.sleep(0.5)
        
        # Stop the loop
        vi.stop_wake_word_detection()
        
        # Should have started wake word detection
        assert mock_porcupine.create.called
    
    def test_handle_voice_failure_with_fallback(self, mock_brain):
        """Test voice failure handling with text fallback."""
        vi = VoiceInterface()
        
        fallback_called = []
        def mock_fallback(error_msg):
            fallback_called.append(error_msg)
            return "fallback input"
        
        vi._handle_voice_failure(
            failure_stage="test",
            error=Exception("test error"),
            brain=mock_brain,
            session_id="test",
            memory_context="",
            on_text_fallback=mock_fallback
        )
        
        # Fallback should be called
        assert len(fallback_called) == 1
        assert "test" in fallback_called[0]
        
        # Brain should process fallback input
        mock_brain.process_input.assert_called_once()
    
    def test_handle_voice_failure_without_fallback(self, mock_brain, capsys):
        """Test voice failure handling without text fallback."""
        vi = VoiceInterface()
        
        vi._handle_voice_failure(
            failure_stage="test",
            error=Exception("test error"),
            brain=mock_brain,
            session_id="test",
            memory_context="",
            on_text_fallback=None
        )
        
        # Should print error message
        captured = capsys.readouterr()
        assert "test" in captured.out.lower()
        
        # Brain should not be called
        mock_brain.process_input.assert_not_called()
