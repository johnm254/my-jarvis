"""Voice Interface - Speech-to-text and text-to-speech functionality.

Wake word detection uses OpenWakeWord (free, no account required).
STT uses OpenAI Whisper (local, private).
TTS uses ElevenLabs API.
"""

import logging
import tempfile
import os
import threading
import time
from typing import Optional, Callable

import whisper
import numpy as np
import sounddevice as sd
import soundfile as sf
from elevenlabs import ElevenLabs, VoiceSettings
from jarvis.metrics import get_metrics_tracker

logger = logging.getLogger(__name__)

# Sample rate required by OpenWakeWord
_OWW_SAMPLE_RATE = 16000
_OWW_CHUNK_SIZE = 1280  # 80ms at 16kHz


class VoiceInterface:
    """
    Voice interface for JARVIS.

    - Wake word: OpenWakeWord (free, open-source, no account needed)
    - STT: OpenAI Whisper (local)
    - TTS: ElevenLabs
    """

    def __init__(
        self,
        model_name: str = "base",
        wake_word: str = "hey_jarvis",
        elevenlabs_api_key: Optional[str] = None,
        voice_id: str = "Rachel",
        # kept for backward-compat but ignored
        porcupine_access_key: Optional[str] = None,
    ):
        self.model_name = model_name
        self.wake_word = wake_word
        self.whisper_model: Optional[whisper.Whisper] = None
        self._wake_word_callback: Optional[Callable] = None
        self._wake_word_thread: Optional[threading.Thread] = None
        self._wake_word_running = False
        self._oww_model = None  # lazy-loaded OpenWakeWord model
        self._elevenlabs_api_key = elevenlabs_api_key
        self._elevenlabs_client: Optional[ElevenLabs] = None
        self._voice_id = voice_id
        self.metrics_tracker = get_metrics_tracker()

        logger.info(f"Initializing VoiceInterface (Whisper={model_name}, wake_word={wake_word})")

        if self._elevenlabs_api_key:
            try:
                self._elevenlabs_client = ElevenLabs(api_key=self._elevenlabs_api_key)
                logger.info(f"ElevenLabs client initialized with voice: {voice_id}")
            except Exception as e:
                logger.warning(f"Failed to initialize ElevenLabs client: {e}")

    # ── Whisper STT ───────────────────────────────────────────────────────────

    def _load_whisper_model(self) -> whisper.Whisper:
        if self.whisper_model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.whisper_model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded")
        return self.whisper_model

    def speech_to_text(self, audio: bytes) -> str:
        if not audio:
            self.metrics_tracker.record_failure("voice.stt")
            return ""

        start = time.time()
        try:
            model = self._load_whisper_model()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio)
                tmp = f.name
            try:
                result = model.transcribe(tmp, fp16=False, language="en")
                text = result["text"].strip()
                self.metrics_tracker.record_latency("voice.stt", (time.time() - start) * 1000)
                self.metrics_tracker.record_success("voice.stt")
                logger.info(f"Transcribed: '{text[:60]}'")
                return text
            finally:
                try:
                    os.unlink(tmp)
                except Exception:
                    pass
        except FileNotFoundError:
            self.metrics_tracker.record_failure("voice.stt")
            logger.error("ffmpeg not found — install it to use STT")
            return ""
        except Exception as e:
            self.metrics_tracker.record_failure("voice.stt")
            logger.error(f"STT failed: {e}", exc_info=True)
            return ""

    # ── OpenWakeWord detection ────────────────────────────────────────────────

    def _load_oww_model(self):
        """Lazy-load OpenWakeWord model."""
        if self._oww_model is None:
            try:
                from openwakeword.model import Model
                # 'hey_jarvis' is a built-in model shipped with openwakeword
                self._oww_model = Model(wakeword_models=[self.wake_word], inference_framework="onnx")
                logger.info(f"OpenWakeWord model loaded: {self.wake_word}")
            except ImportError:
                raise RuntimeError(
                    "openwakeword is not installed. Run: pip install openwakeword"
                )
        return self._oww_model

    def start_wake_word_detection(self) -> None:
        if self._wake_word_running:
            raise RuntimeError("Wake word detection is already running")

        # Pre-load the model before starting the thread
        self._load_oww_model()

        self._wake_word_running = True
        self._wake_word_thread = threading.Thread(
            target=self._wake_word_loop,
            daemon=True,
            name="WakeWordDetection",
        )
        self._wake_word_thread.start()
        logger.info("Wake word detection started (OpenWakeWord)")

    def stop_wake_word_detection(self) -> None:
        if not self._wake_word_running:
            return
        self._wake_word_running = False
        if self._wake_word_thread and self._wake_word_thread.is_alive():
            self._wake_word_thread.join(timeout=3.0)
        logger.info("Wake word detection stopped")

    def _wake_word_loop(self) -> None:
        oww = self._oww_model
        logger.info("Wake word detection loop started")
        try:
            with sd.InputStream(
                samplerate=_OWW_SAMPLE_RATE,
                channels=1,
                dtype="int16",
                blocksize=_OWW_CHUNK_SIZE,
            ) as stream:
                while self._wake_word_running:
                    try:
                        frame, _ = stream.read(_OWW_CHUNK_SIZE)
                        frame_np = frame.flatten().astype(np.int16)
                        prediction = oww.predict(frame_np)
                        # prediction is a dict: {model_name: score}
                        score = prediction.get(self.wake_word, 0.0)
                        if score > 0.5:
                            logger.info(f"Wake word detected! (score={score:.2f})")
                            if self._wake_word_callback:
                                try:
                                    self._wake_word_callback()
                                except Exception as e:
                                    logger.error(f"Wake word callback error: {e}")
                    except Exception as e:
                        logger.error(f"Frame processing error: {e}")
        except Exception as e:
            logger.error(f"Wake word loop error: {e}", exc_info=True)
        finally:
            logger.info("Wake word detection loop ended")

    def on_wake_word_detected(self, callback: Callable) -> None:
        self._wake_word_callback = callback
        logger.info("Wake word callback registered")

    # ── ElevenLabs TTS ────────────────────────────────────────────────────────

    def text_to_speech(self, text: str) -> bytes:
        if not self._elevenlabs_api_key:
            self.metrics_tracker.record_failure("voice.tts")
            raise ValueError("ElevenLabs API key not set")
        if not self._elevenlabs_client:
            self.metrics_tracker.record_failure("voice.tts")
            raise RuntimeError("ElevenLabs client not initialized")
        if not text or not text.strip():
            return b""

        start = time.time()
        try:
            audio_gen = self._elevenlabs_client.text_to_speech.convert(
                voice_id=self._voice_id,
                text=text,
                model_id="eleven_monolingual_v1",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True,
                ),
            )
            audio_bytes = b"".join(audio_gen)
            self.metrics_tracker.record_latency("voice.tts", (time.time() - start) * 1000)
            self.metrics_tracker.record_success("voice.tts")
            logger.info(f"TTS generated {len(audio_bytes)} bytes")
            return audio_bytes
        except Exception as e:
            self.metrics_tracker.record_failure("voice.tts")
            logger.error(f"TTS failed: {e}", exc_info=True)
            raise RuntimeError(f"TTS failed: {e}")

    def play_audio(self, audio: bytes) -> None:
        if not audio:
            raise ValueError("Empty audio")
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio)
            tmp = f.name
        try:
            data, sr = sf.read(tmp)
            sd.play(data, sr)
            sd.wait()
        except Exception as e:
            raise RuntimeError(f"Audio playback failed: {e}")
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass

    # ── Audio recording ───────────────────────────────────────────────────────

    def record_audio(self, duration: float = 5.0, sample_rate: int = 16000) -> bytes:
        logger.info(f"Recording {duration}s of audio...")
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
        )
        sd.wait()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp = f.name
        try:
            sf.write(tmp, audio_data, sample_rate)
            with open(tmp, "rb") as f:
                return f.read()
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass

    # ── Full voice interaction loop ───────────────────────────────────────────

    def voice_interaction_loop(
        self,
        brain,
        session_id: str,
        memory_context: str = "",
        on_text_fallback: Optional[Callable[[str], str]] = None,
        recording_duration: float = 5.0,
    ) -> None:
        """Full pipeline: wake word → STT → Brain → TTS → play."""
        if not self._elevenlabs_api_key or not self._elevenlabs_client:
            raise ValueError("ElevenLabs API key required for voice interaction")
        if brain is None:
            raise ValueError("Brain instance required")

        self._processing_command = False

        def on_wake_word():
            if self._processing_command:
                return
            self._processing_command = True
            try:
                # Record
                try:
                    audio = self.record_audio(duration=recording_duration)
                except Exception as e:
                    logger.error(f"Recording failed: {e}")
                    if on_text_fallback:
                        user_input = on_text_fallback(str(e))
                    else:
                        return
                else:
                    user_input = self.speech_to_text(audio)

                if not user_input:
                    logger.warning("No speech detected")
                    return

                # Brain
                try:
                    tool_defs = None
                    if hasattr(brain, "skill_registry") and brain.skill_registry:
                        tool_defs = brain.skill_registry.get_tool_definitions()
                    resp = brain.process_input(
                        user_input=user_input,
                        session_id=session_id,
                        memory_context=memory_context,
                        tool_definitions=tool_defs,
                    )
                    response_text = resp.text
                except Exception as e:
                    logger.error(f"Brain error: {e}")
                    response_text = "I encountered an error. Please try again."

                # TTS + play
                try:
                    audio_out = self.text_to_speech(response_text)
                    self.play_audio(audio_out)
                except Exception as e:
                    logger.error(f"TTS/playback error: {e}")
                    print(f"\n[JARVIS]: {response_text}\n")
            finally:
                self._processing_command = False

        self.on_wake_word_detected(on_wake_word)
        self.start_wake_word_detection()

        logger.info("Voice interaction loop running. Say 'Hey Jarvis' to activate.")
        print("\n🎤 Listening for 'Hey Jarvis'... (Ctrl+C to stop)\n")
        try:
            while self._wake_word_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_wake_word_detection()
