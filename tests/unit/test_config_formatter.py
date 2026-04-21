"""Unit tests for Config_Formatter."""

import pytest
import tempfile
import os
from pathlib import Path
from jarvis.config import (
    Config_Formatter,
    Config_Parser,
    Configuration,
    format_config_to_env,
    format_config_to_yaml,
)


def create_config_without_env(**kwargs):
    """Create a Configuration object without loading from .env file."""
    # Temporarily disable env_file loading by using model_construct
    # which bypasses validation and env loading
    config_data = {
        'llm_api_key': 'test_key',
        'llm_model': 'claude-sonnet-4-20250514',
        'voice_enabled': True,
        'wake_word': 'Hey Jarvis',
        'stt_model': 'base',
        'tts_api_key': None,
        'supabase_url': 'https://test.supabase.co',
        'supabase_key': 'test_key',
        'brave_api_key': None,
        'google_calendar_credentials': None,
        'gmail_credentials': None,
        'home_assistant_url': None,
        'home_assistant_token': None,
        'github_token': None,
        'weather_api_key': None,
        'dashboard_port': 3000,
        'jwt_secret': 'test_secret',
        'log_level': 'INFO',
        'log_dir': 'logs',
        'timezone': 'UTC',
    }
    config_data.update(kwargs)
    return Configuration.model_construct(**config_data)


class TestConfigFormatterEnv:
    """Test Config_Formatter.to_env_format()."""
    
    def test_format_to_env_with_all_fields(self):
        """Test formatting Configuration with all fields to .env format."""
        config = create_config_without_env(
            llm_api_key="test_api_key_123",
            llm_model="claude-sonnet-4-20250514",
            voice_enabled=True,
            wake_word="Hey Jarvis",
            stt_model="base",
            tts_api_key="elevenlabs_key",
            supabase_url="https://test.supabase.co",
            supabase_key="test_supabase_key",
            brave_api_key="brave_key",
            google_calendar_credentials="/path/to/calendar.json",
            gmail_credentials="/path/to/gmail.json",
            home_assistant_url="http://homeassistant.local:8123",
            home_assistant_token="ha_token",
            github_token="github_token",
            weather_api_key="weather_key",
            dashboard_port=3000,
            jwt_secret="test_jwt_secret",
            log_level="INFO",
            log_dir="logs",
            timezone="UTC",
        )
        
        env_output = Config_Formatter.to_env_format(config)
        
        # Verify required fields are present
        assert "LLM_API_KEY=test_api_key_123" in env_output
        assert "LLM_MODEL=claude-sonnet-4-20250514" in env_output
        assert "VOICE_ENABLED=true" in env_output
        assert "WAKE_WORD=Hey Jarvis" in env_output
        assert "STT_MODEL=base" in env_output
        assert "TTS_API_KEY=elevenlabs_key" in env_output
        assert "SUPABASE_URL=https://test.supabase.co" in env_output
        assert "SUPABASE_KEY=test_supabase_key" in env_output
        assert "BRAVE_API_KEY=brave_key" in env_output
        assert "GOOGLE_CALENDAR_CREDENTIALS=/path/to/calendar.json" in env_output
        assert "GMAIL_CREDENTIALS=/path/to/gmail.json" in env_output
        assert "HOME_ASSISTANT_URL=http://homeassistant.local:8123" in env_output
        assert "HOME_ASSISTANT_TOKEN=ha_token" in env_output
        assert "GITHUB_TOKEN=github_token" in env_output
        assert "WEATHER_API_KEY=weather_key" in env_output
        assert "DASHBOARD_PORT=3000" in env_output
        assert "JWT_SECRET=test_jwt_secret" in env_output
        assert "LOG_LEVEL=INFO" in env_output
        assert "LOG_DIR=logs" in env_output
        assert "TIMEZONE=UTC" in env_output
        
        # Verify comments are present
        assert "# JARVIS Configuration" in env_output
        assert "# LLM Settings" in env_output
        assert "# Voice Settings" in env_output
        assert "# Memory Settings" in env_output
        assert "# API Keys for Skills" in env_output
        assert "# System Settings" in env_output
    
    def test_format_to_env_with_minimal_fields(self):
        """Test formatting Configuration with only required fields to .env format."""
        config = create_config_without_env(
            llm_api_key="test_api_key",
            supabase_url="https://test.supabase.co",
            supabase_key="test_supabase_key",
            jwt_secret="test_jwt_secret",
        )
        
        env_output = Config_Formatter.to_env_format(config)
        
        # Verify required fields are present
        assert "LLM_API_KEY=test_api_key" in env_output
        assert "SUPABASE_URL=https://test.supabase.co" in env_output
        assert "SUPABASE_KEY=test_supabase_key" in env_output
        assert "JWT_SECRET=test_jwt_secret" in env_output
        
        # Verify default values are present
        assert "LLM_MODEL=claude-sonnet-4-20250514" in env_output
        assert "VOICE_ENABLED=true" in env_output
        assert "DASHBOARD_PORT=3000" in env_output
        
        # Verify optional fields are not present when None
        assert "BRAVE_API_KEY" not in env_output
        assert "GOOGLE_CALENDAR_CREDENTIALS" not in env_output
        assert "GMAIL_CREDENTIALS" not in env_output
    
    def test_format_to_env_boolean_values(self):
        """Test formatting boolean values to .env format."""
        config_true = create_config_without_env(
            llm_api_key="test_key",
            supabase_url="https://test.supabase.co",
            supabase_key="test_key",
            jwt_secret="test_secret",
            voice_enabled=True,
        )
        
        config_false = create_config_without_env(
            llm_api_key="test_key",
            supabase_url="https://test.supabase.co",
            supabase_key="test_key",
            jwt_secret="test_secret",
            voice_enabled=False,
        )
        
        env_true = Config_Formatter.to_env_format(config_true)
        env_false = Config_Formatter.to_env_format(config_false)
        
        assert "VOICE_ENABLED=true" in env_true
        assert "VOICE_ENABLED=false" in env_false


class TestConfigFormatterYAML:
    """Test Config_Formatter.to_yaml_format()."""
    
    def test_format_to_yaml_with_all_fields(self):
        """Test formatting Configuration with all fields to YAML format."""
        config = create_config_without_env(
            llm_api_key="test_api_key_123",
            llm_model="claude-sonnet-4-20250514",
            voice_enabled=True,
            wake_word="Hey Jarvis",
            stt_model="base",
            tts_api_key="elevenlabs_key",
            supabase_url="https://test.supabase.co",
            supabase_key="test_supabase_key",
            brave_api_key="brave_key",
            google_calendar_credentials="/path/to/calendar.json",
            gmail_credentials="/path/to/gmail.json",
            home_assistant_url="http://homeassistant.local:8123",
            home_assistant_token="ha_token",
            github_token="github_token",
            weather_api_key="weather_key",
            dashboard_port=3000,
            jwt_secret="test_jwt_secret",
            log_level="INFO",
            log_dir="logs",
            timezone="UTC",
        )
        
        yaml_output = Config_Formatter.to_yaml_format(config)
        
        # Verify required fields are present
        assert "llm_api_key: test_api_key_123" in yaml_output
        assert "llm_model: claude-sonnet-4-20250514" in yaml_output
        assert "voice_enabled: true" in yaml_output
        assert "wake_word: Hey Jarvis" in yaml_output
        assert "stt_model: base" in yaml_output
        assert "tts_api_key: elevenlabs_key" in yaml_output
        assert "supabase_url: https://test.supabase.co" in yaml_output
        assert "supabase_key: test_supabase_key" in yaml_output
        assert "brave_api_key: brave_key" in yaml_output
        assert "google_calendar_credentials: /path/to/calendar.json" in yaml_output
        assert "gmail_credentials: /path/to/gmail.json" in yaml_output
        assert "home_assistant_url: http://homeassistant.local:8123" in yaml_output
        assert "home_assistant_token: ha_token" in yaml_output
        assert "github_token: github_token" in yaml_output
        assert "weather_api_key: weather_key" in yaml_output
        assert "dashboard_port: 3000" in yaml_output
        assert "jwt_secret: test_jwt_secret" in yaml_output
        assert "log_level: INFO" in yaml_output
        assert "log_dir: logs" in yaml_output
        assert "timezone: UTC" in yaml_output
    
    def test_format_to_yaml_with_minimal_fields(self):
        """Test formatting Configuration with only required fields to YAML format."""
        config = create_config_without_env(
            llm_api_key="test_api_key",
            supabase_url="https://test.supabase.co",
            supabase_key="test_supabase_key",
            jwt_secret="test_jwt_secret",
        )
        
        yaml_output = Config_Formatter.to_yaml_format(config)
        
        # Verify required fields are present
        assert "llm_api_key: test_api_key" in yaml_output
        assert "supabase_url: https://test.supabase.co" in yaml_output
        assert "supabase_key: test_supabase_key" in yaml_output
        assert "jwt_secret: test_jwt_secret" in yaml_output
        
        # Verify default values are present
        assert "llm_model: claude-sonnet-4-20250514" in yaml_output
        assert "voice_enabled: true" in yaml_output
        assert "dashboard_port: 3000" in yaml_output
        
        # Verify optional fields are not present when None
        assert "brave_api_key" not in yaml_output
        assert "google_calendar_credentials" not in yaml_output
        assert "gmail_credentials" not in yaml_output
    
    def test_format_to_yaml_boolean_values(self):
        """Test formatting boolean values to YAML format."""
        config_true = create_config_without_env(
            llm_api_key="test_key",
            supabase_url="https://test.supabase.co",
            supabase_key="test_key",
            jwt_secret="test_secret",
            voice_enabled=True,
        )
        
        config_false = create_config_without_env(
            llm_api_key="test_key",
            supabase_url="https://test.supabase.co",
            supabase_key="test_key",
            jwt_secret="test_secret",
            voice_enabled=False,
        )
        
        yaml_true = Config_Formatter.to_yaml_format(config_true)
        yaml_false = Config_Formatter.to_yaml_format(config_false)
        
        assert "voice_enabled: true" in yaml_true
        assert "voice_enabled: false" in yaml_false


class TestConfigFormatterRoundTrip:
    """Test round-trip conversion: format -> parse -> format."""
    
    def test_env_round_trip(self):
        """Test that formatting to .env and parsing back produces equivalent config."""
        original_config = create_config_without_env(
            llm_api_key="test_api_key_123",
            llm_model="claude-sonnet-4-20250514",
            voice_enabled=True,
            wake_word="Hey Jarvis",
            stt_model="base",
            tts_api_key="elevenlabs_key",
            supabase_url="https://test.supabase.co",
            supabase_key="test_supabase_key",
            brave_api_key="brave_key",
            dashboard_port=3000,
            jwt_secret="test_jwt_secret",
            log_level="INFO",
            log_dir="logs",
            timezone="UTC",
        )
        
        # Format to .env
        env_output = Config_Formatter.to_env_format(original_config)
        
        # Write to temp file and parse back
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_output)
            f.flush()
            temp_path = f.name
        
        try:
            parsed_config = Config_Parser.parse_env_file(temp_path)
            
            # Verify all fields match
            assert parsed_config.llm_api_key == original_config.llm_api_key
            assert parsed_config.llm_model == original_config.llm_model
            assert parsed_config.voice_enabled == original_config.voice_enabled
            assert parsed_config.wake_word == original_config.wake_word
            assert parsed_config.stt_model == original_config.stt_model
            assert parsed_config.tts_api_key == original_config.tts_api_key
            assert parsed_config.supabase_url == original_config.supabase_url
            assert parsed_config.supabase_key == original_config.supabase_key
            assert parsed_config.brave_api_key == original_config.brave_api_key
            assert parsed_config.dashboard_port == original_config.dashboard_port
            assert parsed_config.jwt_secret == original_config.jwt_secret
            assert parsed_config.log_level == original_config.log_level
            assert parsed_config.log_dir == original_config.log_dir
            assert parsed_config.timezone == original_config.timezone
        finally:
            Path(temp_path).unlink()
    
    def test_yaml_round_trip(self):
        """Test that formatting to YAML and parsing back produces equivalent config."""
        original_config = create_config_without_env(
            llm_api_key="test_api_key_123",
            llm_model="claude-sonnet-4-20250514",
            voice_enabled=True,
            wake_word="Hey Jarvis",
            stt_model="base",
            tts_api_key="elevenlabs_key",
            supabase_url="https://test.supabase.co",
            supabase_key="test_supabase_key",
            brave_api_key="brave_key",
            dashboard_port=3000,
            jwt_secret="test_jwt_secret",
            log_level="INFO",
            log_dir="logs",
            timezone="UTC",
        )
        
        # Format to YAML
        yaml_output = Config_Formatter.to_yaml_format(original_config)
        
        # Write to temp file and parse back
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_output)
            f.flush()
            temp_path = f.name
        
        try:
            parsed_config = Config_Parser.parse_yaml_file(temp_path)
            
            # Verify all fields match
            assert parsed_config.llm_api_key == original_config.llm_api_key
            assert parsed_config.llm_model == original_config.llm_model
            assert parsed_config.voice_enabled == original_config.voice_enabled
            assert parsed_config.wake_word == original_config.wake_word
            assert parsed_config.stt_model == original_config.stt_model
            assert parsed_config.tts_api_key == original_config.tts_api_key
            assert parsed_config.supabase_url == original_config.supabase_url
            assert parsed_config.supabase_key == original_config.supabase_key
            assert parsed_config.brave_api_key == original_config.brave_api_key
            assert parsed_config.dashboard_port == original_config.dashboard_port
            assert parsed_config.jwt_secret == original_config.jwt_secret
            assert parsed_config.log_level == original_config.log_level
            assert parsed_config.log_dir == original_config.log_dir
            assert parsed_config.timezone == original_config.timezone
        finally:
            Path(temp_path).unlink()
    
    def test_env_round_trip_minimal_config(self):
        """Test round-trip with minimal configuration (only required fields)."""
        original_config = create_config_without_env(
            llm_api_key="test_api_key",
            supabase_url="https://test.supabase.co",
            supabase_key="test_supabase_key",
            jwt_secret="test_jwt_secret",
        )
        
        # Format to .env
        env_output = Config_Formatter.to_env_format(original_config)
        
        # Write to temp file and parse back
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_output)
            f.flush()
            temp_path = f.name
        
        try:
            parsed_config = Config_Parser.parse_env_file(temp_path)
            
            # Verify required fields match
            assert parsed_config.llm_api_key == original_config.llm_api_key
            assert parsed_config.supabase_url == original_config.supabase_url
            assert parsed_config.supabase_key == original_config.supabase_key
            assert parsed_config.jwt_secret == original_config.jwt_secret
            
            # Verify defaults are preserved
            assert parsed_config.llm_model == original_config.llm_model
            assert parsed_config.voice_enabled == original_config.voice_enabled
            assert parsed_config.dashboard_port == original_config.dashboard_port
        finally:
            Path(temp_path).unlink()


class TestConvenienceFunctions:
    """Test convenience functions for formatting."""
    
    def test_format_config_to_env(self):
        """Test format_config_to_env convenience function."""
        config = create_config_without_env(
            llm_api_key="test_key",
            supabase_url="https://test.supabase.co",
            supabase_key="test_key",
            jwt_secret="test_secret",
        )
        
        env_output = format_config_to_env(config)
        
        assert "LLM_API_KEY=test_key" in env_output
        assert "SUPABASE_URL=https://test.supabase.co" in env_output
    
    def test_format_config_to_yaml(self):
        """Test format_config_to_yaml convenience function."""
        config = create_config_without_env(
            llm_api_key="test_key",
            supabase_url="https://test.supabase.co",
            supabase_key="test_key",
            jwt_secret="test_secret",
        )
        
        yaml_output = format_config_to_yaml(config)
        
        assert "llm_api_key: test_key" in yaml_output
        assert "supabase_url: https://test.supabase.co" in yaml_output


class TestFormatterOutputValidity:
    """Test that formatter output is valid and parseable."""
    
    def test_env_output_is_parseable(self):
        """Test that .env output can be parsed without errors."""
        config = create_config_without_env(
            llm_api_key="test_key_with_special_chars!@#",
            supabase_url="https://test.supabase.co?param=value&other=123",
            supabase_key="test_key",
            jwt_secret="test_secret",
        )
        
        env_output = Config_Formatter.to_env_format(config)
        
        # Write to temp file and verify it can be parsed
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_output)
            f.flush()
            temp_path = f.name
        
        try:
            # Should not raise any exception
            parsed_config = Config_Parser.parse_env_file(temp_path)
            assert parsed_config.llm_api_key == config.llm_api_key
            assert parsed_config.supabase_url == config.supabase_url
        finally:
            Path(temp_path).unlink()
    
    def test_yaml_output_is_parseable(self):
        """Test that YAML output can be parsed without errors."""
        config = create_config_without_env(
            llm_api_key="test_key_with_special_chars!@#",
            supabase_url="https://test.supabase.co?param=value&other=123",
            supabase_key="test_key",
            jwt_secret="test_secret",
        )
        
        yaml_output = Config_Formatter.to_yaml_format(config)
        
        # Write to temp file and verify it can be parsed
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_output)
            f.flush()
            temp_path = f.name
        
        try:
            # Should not raise any exception
            parsed_config = Config_Parser.parse_yaml_file(temp_path)
            assert parsed_config.llm_api_key == config.llm_api_key
            assert parsed_config.supabase_url == config.supabase_url
        finally:
            Path(temp_path).unlink()
