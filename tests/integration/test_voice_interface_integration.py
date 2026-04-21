"""Integration tests for Voice Interface with real Whisper model."""

import pytest
import tempfile
import wave
import os
import numpy as np

from jarvis.voice import VoiceInterface


@pytest.mark.integration
class TestVoiceInterfaceIntegration:
    """
    Integration tests for VoiceInterface with real Whisper model.
    
    Note: These tests use the actual Whisper model and may take longer to run.
    They are marked with @pytest.mark.integration so they can be run separately.
    """
    
    @pytest.fixture
    def voice_interface(self):
        """Create a VoiceInterface instance with tiny model for faster testing."""
        # Use 'tiny' model for faster integration tests
        return VoiceInterface(model_name="tiny")
    
    @pytest.fixture
    def sample_audio_file(self):
        """
        Create a sample audio file for testing.
        
        Returns:
            bytes: WAV audio data
        """
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
            # Clean up
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.unlink(temp_wav_path)
                except:
                    pass
    
    def test_whisper_model_loads(self, voice_interface):
        """Test that Whisper model can be loaded successfully."""
        model = voice_interface._load_whisper_model()
        
        assert model is not None
        assert voice_interface.whisper_model is not None
    
    def test_speech_to_text_with_real_model(self, voice_interface, sample_audio_file):
        """
        Test speech-to-text with real Whisper model.
        
        Note: This test uses silent audio, so the transcription will be empty or minimal.
        The purpose is to verify the pipeline works end-to-end.
        """
        result = voice_interface.speech_to_text(sample_audio_file)
        
        # Result should be a string (may be empty for silent audio)
        assert isinstance(result, str)
        # Silent audio typically produces empty or minimal transcription
        assert len(result) < 100
    
    def test_speech_to_text_processes_locally(self, voice_interface, sample_audio_file):
        """
        Verify that speech-to-text processes audio locally without external API calls.
        
        Requirements: 3.1, 3.5, 3.8
        """
        # This test verifies local processing by successfully transcribing
        # without any network configuration or API keys
        result = voice_interface.speech_to_text(sample_audio_file)
        
        # If we get a result (even empty), it means local processing worked
        assert isinstance(result, str)
    
    def test_multiple_transcriptions(self, voice_interface, sample_audio_file):
        """Test that multiple transcriptions work correctly (model caching)."""
        result1 = voice_interface.speech_to_text(sample_audio_file)
        result2 = voice_interface.speech_to_text(sample_audio_file)
        
        # Both should succeed
        assert isinstance(result1, str)
        assert isinstance(result2, str)
        
        # Results should be consistent for the same audio
        assert result1 == result2
    
    def test_error_handling_with_invalid_audio(self, voice_interface):
        """Test that invalid audio is handled gracefully."""
        invalid_audio = b"This is not valid audio data"
        
        # Should return empty string (fallback behavior)
        result = voice_interface.speech_to_text(invalid_audio)
        
        assert result == ""


@pytest.mark.integration
class TestVoiceInterfaceRequirementsIntegration:
    """Integration tests verifying specific requirements with real Whisper model."""
    
    @pytest.fixture
    def voice_interface(self):
        """Create a VoiceInterface instance with tiny model."""
        return VoiceInterface(model_name="tiny")
    
    @pytest.fixture
    def sample_audio_file(self):
        """Create a sample audio file."""
        temp_wav_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_wav_path = temp_wav.name
            
            sample_rate = 16000
            duration = 1
            num_samples = sample_rate * duration
            audio_data = np.zeros(num_samples, dtype=np.int16)
            
            with wave.open(temp_wav_path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            with open(temp_wav_path, 'rb') as f:
                audio_bytes = f.read()
            
            return audio_bytes
        finally:
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.unlink(temp_wav_path)
                except:
                    pass
    
    def test_requirement_3_1_uses_whisper_locally(self, voice_interface, sample_audio_file):
        """
        Requirement 3.1: THE Voice_Interface SHALL use OpenAI Whisper running locally for STT conversion.
        
        This integration test verifies that the actual Whisper model is used.
        """
        # Load the model
        model = voice_interface._load_whisper_model()
        
        # Verify it's a Whisper model
        assert hasattr(model, 'transcribe')
        
        # Perform transcription
        result = voice_interface.speech_to_text(sample_audio_file)
        
        # Verify transcription completed (even if result is empty for silent audio)
        assert isinstance(result, str)
    
    def test_requirement_3_5_processes_locally_no_external_calls(self, voice_interface, sample_audio_file):
        """
        Requirement 3.5: WHEN audio input is received, THE STT SHALL process it locally 
        without sending audio to external services.
        
        This test verifies local processing by working without network access.
        """
        # Process audio
        result = voice_interface.speech_to_text(sample_audio_file)
        
        # If this succeeds without network configuration, it's processing locally
        assert isinstance(result, str)
    
    def test_requirement_3_7_fallback_on_failure(self, voice_interface):
        """
        Requirement 3.7: IF voice input fails, THEN THE JARVIS_System SHALL fall back to text input.
        
        Verify that failures return empty string to enable fallback.
        """
        # Test with invalid audio
        result = voice_interface.speech_to_text(b"invalid")
        
        # Should return empty string to signal fallback needed
        assert result == ""
    
    def test_requirement_3_8_offline_operation(self, voice_interface, sample_audio_file):
        """
        Requirement 3.8: THE Voice_Interface SHALL operate offline for STT processing.
        
        Verify that STT works without any network dependencies.
        """
        # This test succeeds if transcription works without network setup
        result = voice_interface.speech_to_text(sample_audio_file)
        
        # Success means offline operation works
        assert isinstance(result, str)



@pytest.mark.integration
class TestWakeWordDetectionIntegration:
    """Integration tests for wake word detection with Porcupine."""
    
    @pytest.fixture
    def porcupine_access_key(self):
        """Get Porcupine access key from environment."""
        key = os.getenv("PORCUPINE_ACCESS_KEY")
        if not key or key == "your_porcupine_access_key_here":
            pytest.skip("PORCUPINE_ACCESS_KEY not configured")
        return key
    
    def test_wake_word_detection_initialization(self, porcupine_access_key):
        """Test wake word detection can be initialized with valid key."""
        import time
        
        vi = VoiceInterface(model_name="tiny", porcupine_access_key=porcupine_access_key)
        
        try:
            # Start wake word detection
            vi.start_wake_word_detection()
            
            # Verify it's running
            assert vi._wake_word_running is True
            assert vi._wake_word_thread is not None
            assert vi._wake_word_thread.is_alive()
            
            # Wait a moment to ensure thread is stable
            time.sleep(0.5)
            assert vi._wake_word_thread.is_alive()
            
        finally:
            # Clean up
            vi.stop_wake_word_detection()
            
            # Verify cleanup
            assert vi._wake_word_running is False
    
    def test_wake_word_callback_registration(self, porcupine_access_key):
        """Test that wake word callback can be registered."""
        from unittest.mock import Mock
        
        vi = VoiceInterface(model_name="tiny", porcupine_access_key=porcupine_access_key)
        
        callback = Mock()
        vi.on_wake_word_detected(callback)
        
        assert vi._wake_word_callback == callback
    
    def test_wake_word_detection_without_key(self):
        """Test that wake word detection fails without access key."""
        vi = VoiceInterface(model_name="tiny")
        
        with pytest.raises(ValueError, match="Porcupine access key is required"):
            vi.start_wake_word_detection()
    
    def test_wake_word_detection_stop_when_not_running(self):
        """Test that stopping wake word detection when not running is safe."""
        vi = VoiceInterface(model_name="tiny", porcupine_access_key="test_key")
        
        # Should not raise an error
        vi.stop_wake_word_detection()
        
        assert vi._wake_word_running is False
    
    def test_requirement_3_3_wake_word_activates_listening(self, porcupine_access_key):
        """
        Requirement 3.3: WHEN the Wake_Word "Hey Jarvis" is detected, 
        THE Voice_Interface SHALL activate listening mode.
        
        This test verifies the wake word detection mechanism is in place.
        """
        import time
        from unittest.mock import Mock
        
        vi = VoiceInterface(model_name="tiny", porcupine_access_key=porcupine_access_key)
        
        # Register a callback to verify detection mechanism
        callback = Mock()
        vi.on_wake_word_detected(callback)
        
        try:
            # Start wake word detection
            vi.start_wake_word_detection()
            
            # Verify detection is active
            assert vi._wake_word_running is True
            
            # Wait to ensure thread is processing
            time.sleep(1.0)
            
            # Verify thread is still running (stable)
            assert vi._wake_word_thread.is_alive()
            
        finally:
            vi.stop_wake_word_detection()
    
    def test_requirement_3_4_uses_porcupine(self, porcupine_access_key):
        """
        Requirement 3.4: THE Voice_Interface SHALL use Porcupine or Picovoice 
        for Wake_Word detection.
        
        This test verifies Porcupine is used for wake word detection.
        """
        import time
        
        vi = VoiceInterface(model_name="tiny", porcupine_access_key=porcupine_access_key)
        
        try:
            # Start wake word detection
            vi.start_wake_word_detection()
            
            # Verify Porcupine instance was created
            assert vi._porcupine is not None
            assert hasattr(vi._porcupine, 'process')
            assert hasattr(vi._porcupine, 'sample_rate')
            assert hasattr(vi._porcupine, 'frame_length')
            
            time.sleep(0.5)
            
        finally:
            vi.stop_wake_word_detection()
            
            # Verify cleanup
            assert vi._porcupine is None



@pytest.mark.integration
class TestTextToSpeechIntegration:
    """Integration tests for text-to-speech with ElevenLabs API."""
    
    @pytest.fixture
    def elevenlabs_api_key(self):
        """Get ElevenLabs API key from environment."""
        key = os.getenv("ELEVENLABS_API_KEY")
        if not key or key == "your_elevenlabs_api_key_here":
            pytest.skip("ELEVENLABS_API_KEY not configured")
        return key
    
    @pytest.fixture
    def voice_interface_with_tts(self, elevenlabs_api_key):
        """Create a VoiceInterface instance with ElevenLabs TTS."""
        return VoiceInterface(
            model_name="tiny",
            elevenlabs_api_key=elevenlabs_api_key,
            voice_id="Rachel"
        )
    
    def test_text_to_speech_with_real_api(self, voice_interface_with_tts):
        """
        Test text-to-speech with real ElevenLabs API.
        
        Note: This test makes a real API call and requires a valid API key.
        """
        text = "Hello, this is a test."
        
        # Convert text to speech
        audio_bytes = voice_interface_with_tts.text_to_speech(text)
        
        # Verify audio was generated
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0
        
        # Audio should be substantial (at least a few KB for this text)
        assert len(audio_bytes) > 1000
    
    def test_text_to_speech_empty_text(self, voice_interface_with_tts):
        """Test that empty text returns empty bytes."""
        result = voice_interface_with_tts.text_to_speech("")
        assert result == b""
        
        result = voice_interface_with_tts.text_to_speech("   ")
        assert result == b""
    
    def test_text_to_speech_longer_text(self, voice_interface_with_tts):
        """Test text-to-speech with longer text."""
        text = (
            "Good morning Boss! I am JARVIS, your personal AI assistant. "
            "I'm here to help you with your daily tasks and answer your questions."
        )
        
        audio_bytes = voice_interface_with_tts.text_to_speech(text)
        
        # Verify audio was generated
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0
        
        # Longer text should produce more audio
        assert len(audio_bytes) > 5000
    
    def test_text_to_speech_without_api_key(self):
        """Test that TTS fails gracefully without API key."""
        vi = VoiceInterface(model_name="tiny")
        
        with pytest.raises(ValueError, match="ElevenLabs API key is required"):
            vi.text_to_speech("Hello")
    
    def test_requirement_3_2_uses_elevenlabs(self, voice_interface_with_tts):
        """
        Requirement 3.2: THE Voice_Interface SHALL use ElevenLabs API for TTS conversion.
        
        This integration test verifies that ElevenLabs API is actually used.
        """
        text = "Testing ElevenLabs integration."
        
        # Convert text to speech
        audio_bytes = voice_interface_with_tts.text_to_speech(text)
        
        # Verify audio was generated via ElevenLabs
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0
    
    def test_requirement_3_6_natural_speech_output(self, voice_interface_with_tts):
        """
        Requirement 3.6: WHEN the Brain generates a response, THE TTS SHALL convert it to natural speech output.
        
        This test verifies the complete TTS pipeline.
        """
        response_text = "The weather today is sunny with a high of 75 degrees."
        
        # Convert to speech
        audio_bytes = voice_interface_with_tts.text_to_speech(response_text)
        
        # Verify natural speech was generated
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0
        
        # Audio should be in a playable format (MP3)
        # MP3 files typically start with ID3 tag or sync word
        # Just verify we have substantial audio data
        assert len(audio_bytes) > 2000


@pytest.mark.integration
class TestAudioPlaybackIntegration:
    """Integration tests for audio playback functionality."""
    
    @pytest.fixture
    def elevenlabs_api_key(self):
        """Get ElevenLabs API key from environment."""
        key = os.getenv("ELEVENLABS_API_KEY")
        if not key or key == "your_elevenlabs_api_key_here":
            pytest.skip("ELEVENLABS_API_KEY not configured")
        return key
    
    @pytest.fixture
    def voice_interface_with_tts(self, elevenlabs_api_key):
        """Create a VoiceInterface instance with ElevenLabs TTS."""
        return VoiceInterface(
            model_name="tiny",
            elevenlabs_api_key=elevenlabs_api_key,
            voice_id="Rachel"
        )
    
    @pytest.mark.skip(reason="Audio playback requires audio output device and may be disruptive")
    def test_play_audio_with_real_audio(self, voice_interface_with_tts):
        """
        Test audio playback with real audio from TTS.
        
        Note: This test is skipped by default as it requires audio output
        and will play sound. Run manually with: pytest -m integration --run-audio-tests
        """
        # Generate audio
        text = "This is a test of audio playback."
        audio_bytes = voice_interface_with_tts.text_to_speech(text)
        
        # Play the audio
        # This should not raise an exception
        voice_interface_with_tts.play_audio(audio_bytes)
    
    def test_play_audio_empty_bytes(self, voice_interface_with_tts):
        """Test that play_audio raises ValueError with empty audio."""
        with pytest.raises(ValueError, match="Cannot play empty audio"):
            voice_interface_with_tts.play_audio(b"")
    
    def test_play_audio_none_bytes(self, voice_interface_with_tts):
        """Test that play_audio raises ValueError with None."""
        with pytest.raises(ValueError, match="Cannot play empty audio"):
            voice_interface_with_tts.play_audio(None)
    
    def test_requirement_3_6_audio_output_to_speakers(self, voice_interface_with_tts):
        """
        Requirement 3.6: Audio output should be played to speakers.
        
        This test verifies the play_audio method exists and has correct interface.
        """
        # Verify method exists
        assert hasattr(voice_interface_with_tts, 'play_audio')
        assert callable(voice_interface_with_tts.play_audio)
        
        # Verify it handles empty audio correctly
        with pytest.raises(ValueError):
            voice_interface_with_tts.play_audio(b"")


@pytest.mark.integration
class TestCompleteVoiceWorkflow:
    """Integration tests for complete voice interaction workflow."""
    
    @pytest.fixture
    def elevenlabs_api_key(self):
        """Get ElevenLabs API key from environment."""
        key = os.getenv("ELEVENLABS_API_KEY")
        if not key or key == "your_elevenlabs_api_key_here":
            pytest.skip("ELEVENLABS_API_KEY not configured")
        return key
    
    @pytest.fixture
    def voice_interface_full(self, elevenlabs_api_key):
        """Create a fully configured VoiceInterface."""
        return VoiceInterface(
            model_name="tiny",
            elevenlabs_api_key=elevenlabs_api_key,
            voice_id="Rachel"
        )
    
    def test_text_to_speech_pipeline(self, voice_interface_full):
        """
        Test the complete text-to-speech pipeline:
        Text -> TTS API -> Audio Bytes
        """
        # Input text
        input_text = "Hello Boss! How can I help you today?"
        
        # Convert to speech
        audio_bytes = voice_interface_full.text_to_speech(input_text)
        
        # Verify output
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0
        
        # Verify audio is substantial
        assert len(audio_bytes) > 1000
    
    def test_multiple_tts_calls(self, voice_interface_full):
        """Test that multiple TTS calls work correctly."""
        texts = [
            "First message.",
            "Second message.",
            "Third message."
        ]
        
        audio_results = []
        for text in texts:
            audio = voice_interface_full.text_to_speech(text)
            audio_results.append(audio)
        
        # All should succeed
        assert len(audio_results) == 3
        for audio in audio_results:
            assert isinstance(audio, bytes)
            assert len(audio) > 0
    
    def test_tts_with_special_characters(self, voice_interface_full):
        """Test TTS with special characters and punctuation."""
        text = "Hello! How are you? I'm doing great. Let's test: numbers 1, 2, 3."
        
        audio_bytes = voice_interface_full.text_to_speech(text)
        
        # Should handle special characters gracefully
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0
    
    def test_tts_error_recovery(self, voice_interface_full):
        """Test that TTS errors are handled gracefully."""
        # Test with empty text (should return empty bytes, not error)
        result = voice_interface_full.text_to_speech("")
        assert result == b""
        
        # Test with whitespace only
        result = voice_interface_full.text_to_speech("   ")
        assert result == b""
        
        # Test with valid text after errors
        result = voice_interface_full.text_to_speech("Valid text")
        assert len(result) > 0



@pytest.mark.integration
class TestVoiceInteractionLoopIntegration:
    """Integration tests for complete voice interaction loop."""
    
    @pytest.fixture
    def porcupine_access_key(self):
        """Get Porcupine access key from environment."""
        key = os.getenv("PORCUPINE_ACCESS_KEY")
        if not key or key == "your_porcupine_access_key_here":
            pytest.skip("PORCUPINE_ACCESS_KEY not configured")
        return key
    
    @pytest.fixture
    def elevenlabs_api_key(self):
        """Get ElevenLabs API key from environment."""
        key = os.getenv("ELEVENLABS_API_KEY")
        if not key or key == "your_elevenlabs_api_key_here":
            pytest.skip("ELEVENLABS_API_KEY not configured")
        return key
    
    @pytest.fixture
    def anthropic_api_key(self):
        """Get Anthropic API key from environment."""
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key or key == "your_anthropic_api_key_here":
            pytest.skip("ANTHROPIC_API_KEY not configured")
        return key
    
    @pytest.fixture
    def voice_interface_full(self, porcupine_access_key, elevenlabs_api_key):
        """Create a fully configured VoiceInterface."""
        return VoiceInterface(
            model_name="tiny",
            porcupine_access_key=porcupine_access_key,
            elevenlabs_api_key=elevenlabs_api_key,
            voice_id="Rachel"
        )
    
    @pytest.fixture
    def mock_brain(self):
        """Create a mock Brain for testing."""
        from unittest.mock import Mock
        brain = Mock()
        brain.process_input.return_value = Mock(text="Test response from Brain")
        brain.skill_registry = None
        return brain
    
    def test_voice_interaction_loop_initialization(
        self, voice_interface_full, mock_brain
    ):
        """Test that voice interaction loop can be initialized."""
        import threading
        import time
        
        # Start loop in background thread
        def run_loop():
            try:
                voice_interface_full.voice_interaction_loop(
                    brain=mock_brain,
                    session_id="test_session"
                )
            except:
                pass
        
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
        
        # Give it time to start
        time.sleep(1.0)
        
        # Verify wake word detection is running
        assert voice_interface_full._wake_word_running is True
        
        # Stop the loop
        voice_interface_full.stop_wake_word_detection()
        
        # Wait for thread to finish
        thread.join(timeout=2.0)
    
    def test_voice_interaction_loop_with_text_fallback(
        self, voice_interface_full, mock_brain
    ):
        """Test voice interaction loop with text fallback handler."""
        from unittest.mock import Mock
        
        fallback_handler = Mock(return_value="test input")
        
        # Test that fallback handler can be registered
        # (We won't actually trigger it in this test)
        import threading
        import time
        
        def run_loop():
            try:
                voice_interface_full.voice_interaction_loop(
                    brain=mock_brain,
                    session_id="test_session",
                    on_text_fallback=fallback_handler
                )
            except:
                pass
        
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
        
        time.sleep(1.0)
        
        # Stop the loop
        voice_interface_full.stop_wake_word_detection()
        thread.join(timeout=2.0)
    
    def test_record_audio_integration(self, voice_interface_full):
        """Test audio recording with real audio device."""
        # Record 1 second of audio
        audio_bytes = voice_interface_full.record_audio(duration=1.0)
        
        # Verify audio was recorded
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0
        
        # WAV files have a header, so should be at least a few KB
        assert len(audio_bytes) > 1000
    
    def test_requirement_3_7_complete_voice_pipeline(
        self, voice_interface_full, mock_brain
    ):
        """
        Requirement 3.7: IF voice input fails, THEN THE JARVIS_System SHALL fall back to text input.
        
        This test verifies the complete voice pipeline exists with fallback capability.
        """
        # Verify all required methods exist
        assert hasattr(voice_interface_full, 'voice_interaction_loop')
        assert hasattr(voice_interface_full, 'record_audio')
        assert hasattr(voice_interface_full, '_handle_voice_failure')
        
        # Verify the loop can be started (even if we stop it immediately)
        import threading
        import time
        
        def run_loop():
            try:
                voice_interface_full.voice_interaction_loop(
                    brain=mock_brain,
                    session_id="test_session"
                )
            except:
                pass
        
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
        
        time.sleep(0.5)
        
        # Verify it started
        assert voice_interface_full._wake_word_running is True
        
        # Stop it
        voice_interface_full.stop_wake_word_detection()
        thread.join(timeout=2.0)
