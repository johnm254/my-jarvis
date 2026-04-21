"""Configuration management for JARVIS."""

import os
from pathlib import Path
from typing import Optional, Union
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class Configuration(BaseSettings):
    """JARVIS system configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM Settings
    llm_api_key: str = Field(..., description="LLM API key for reasoning engine")
    llm_model: str = Field(
        default="llama-3.3-70b-versatile", description="LLM model to use"
    )

    # Voice Settings
    voice_enabled: bool = Field(default=True, description="Enable voice interaction")
    wake_word: str = Field(default="Hey Jarvis", description="Wake word for activation")
    stt_model: str = Field(default="base", description="Whisper model size")
    tts_api_key: Optional[str] = Field(
        default=None, description="TTS API key (e.g., ElevenLabs)"
    )

    # Memory Settings
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase anon/service key")

    # API Keys for Skills
    brave_api_key: Optional[str] = Field(default=None, description="Brave Search API key")
    google_calendar_credentials: Optional[str] = Field(
        default=None, description="Path to Google Calendar credentials"
    )
    gmail_credentials: Optional[str] = Field(
        default=None, description="Path to Gmail credentials"
    )
    home_assistant_url: Optional[str] = Field(
        default=None, description="Home Assistant instance URL"
    )
    home_assistant_token: Optional[str] = Field(
        default=None, description="Home Assistant access token"
    )
    github_token: Optional[str] = Field(default=None, description="GitHub personal access token")
    weather_api_key: Optional[str] = Field(default=None, description="Weather API key")

    # System Settings
    dashboard_port: int = Field(default=3000, description="Dashboard web server port")
    jwt_secret: str = Field(..., description="JWT secret for dashboard authentication")
    log_level: str = Field(default="INFO", description="Logging level")
    log_dir: str = Field(default="logs", description="Directory for log files")
    timezone: str = Field(default="UTC", description="System timezone")


class ConfigParseError(Exception):
    """Exception raised when configuration parsing fails."""
    pass


class Config_Parser:
    """Parser for .env and YAML configuration files."""
    
    @staticmethod
    def parse_env_file(file_path: Union[str, Path]) -> Configuration:
        """
        Parse a .env file into a Configuration object.
        
        Args:
            file_path: Path to the .env file
            
        Returns:
            Configuration object with parsed values
            
        Raises:
            ConfigParseError: If file doesn't exist, is malformed, or validation fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ConfigParseError(f"Configuration file not found: {file_path}")
        
        try:
            # Read the .env file and set environment variables temporarily
            env_vars = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' not in line:
                        raise ConfigParseError(
                            f"Invalid format at line {line_num}: '{line}'. "
                            f"Expected KEY=VALUE format."
                        )
                    
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Normalize key to lowercase for Configuration field matching
                    env_vars[key.lower()] = value
            
            # Create Configuration from parsed environment variables
            return Config_Parser._create_config_from_dict(env_vars, file_path)
            
        except ConfigParseError:
            raise
        except Exception as e:
            raise ConfigParseError(f"Error parsing .env file '{file_path}': {str(e)}")
    
    @staticmethod
    def parse_yaml_file(file_path: Union[str, Path]) -> Configuration:
        """
        Parse a YAML configuration file into a Configuration object.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Configuration object with parsed values
            
        Raises:
            ConfigParseError: If file doesn't exist, is malformed, or validation fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ConfigParseError(f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if yaml_data is None:
                raise ConfigParseError(f"YAML file is empty: {file_path}")
            
            if not isinstance(yaml_data, dict):
                raise ConfigParseError(
                    f"Invalid YAML format in '{file_path}': "
                    f"Expected a dictionary at root level, got {type(yaml_data).__name__}"
                )
            
            # Convert YAML keys to lowercase to match Configuration field names
            normalized_data = {k.lower(): v for k, v in yaml_data.items()}
            
            return Config_Parser._create_config_from_dict(normalized_data, file_path)
            
        except yaml.YAMLError as e:
            raise ConfigParseError(f"Invalid YAML syntax in '{file_path}': {str(e)}")
        except ConfigParseError:
            raise
        except Exception as e:
            raise ConfigParseError(f"Error parsing YAML file '{file_path}': {str(e)}")
    
    @staticmethod
    def _create_config_from_dict(data: dict, source_file: Path) -> Configuration:
        """
        Create a Configuration object from a dictionary with validation.
        
        Args:
            data: Dictionary of configuration values
            source_file: Source file path for error messages
            
        Returns:
            Configuration object
            
        Raises:
            ConfigParseError: If validation fails
        """
        try:
            # Temporarily disable env_file loading by using construct
            # which bypasses validation and env loading, then validate manually
            # We need to ensure required fields are present
            required_fields = ['llm_api_key', 'supabase_url', 'supabase_key', 'jwt_secret']
            missing_fields = [f for f in required_fields if f not in data or data[f] is None]
            
            if missing_fields:
                raise ValidationError.from_exception_data(
                    'Configuration',
                    [{'type': 'missing', 'loc': (field,), 'msg': 'Field required', 'input': data}
                     for field in missing_fields]
                )
            
            # Now create the configuration - it will still load from env but we've checked required fields
            config = Configuration(**data)
            
            # Override with our parsed values to ensure we're using the file data, not env
            # Pydantic will handle type conversion
            for key, value in data.items():
                # Get the field info to check the type
                field_info = Configuration.model_fields.get(key)
                if field_info:
                    # Let Pydantic handle the conversion by validating the single field
                    try:
                        if field_info.annotation == int:
                            value = int(value) if isinstance(value, str) else value
                        elif field_info.annotation == bool:
                            if isinstance(value, str):
                                value = value.lower() in ('true', '1', 'yes', 'on')
                    except (ValueError, AttributeError):
                        pass  # Let Pydantic's validation catch this
                setattr(config, key, value)
            
            return config
            
        except ValidationError as e:
            # Format validation errors into a descriptive message
            error_messages = []
            for error in e.errors():
                field = error['loc'][0] if error['loc'] else 'unknown'
                msg = error['msg']
                error_type = error['type']
                
                if error_type == 'missing':
                    error_messages.append(f"Missing required field: '{field}'")
                elif error_type in ('type_error.integer', 'int_parsing'):
                    error_messages.append(
                        f"Invalid type for field '{field}': expected integer, got {error.get('input', 'invalid value')}"
                    )
                elif error_type in ('type_error.bool', 'bool_parsing'):
                    error_messages.append(
                        f"Invalid type for field '{field}': expected boolean (true/false), got {error.get('input', 'invalid value')}"
                    )
                elif error_type in ('type_error.str', 'string_type'):
                    error_messages.append(
                        f"Invalid type for field '{field}': expected string"
                    )
                else:
                    error_messages.append(f"Validation error for field '{field}': {msg}")
            
            raise ConfigParseError(
                f"Configuration validation failed for '{source_file}':\n" +
                "\n".join(f"  - {msg}" for msg in error_messages)
            )


def load_config() -> Configuration:
    """Load configuration from environment variables."""
    return Configuration()


class Config_Formatter:
    """Formatter for converting Configuration objects to .env and YAML formats."""
    
    @staticmethod
    def to_env_format(config: Configuration) -> str:
        """
        Convert a Configuration object to .env format.
        
        Args:
            config: Configuration object to format
            
        Returns:
            String in .env format with KEY=VALUE pairs
        """
        lines = []
        
        # Add header comment
        lines.append("# JARVIS Configuration")
        lines.append("")
        
        # LLM Settings
        lines.append("# LLM Settings")
        lines.append(f"LLM_API_KEY={config.llm_api_key}")
        lines.append(f"LLM_MODEL={config.llm_model}")
        lines.append("")
        
        # Voice Settings
        lines.append("# Voice Settings")
        lines.append(f"VOICE_ENABLED={str(config.voice_enabled).lower()}")
        lines.append(f"WAKE_WORD={config.wake_word}")
        lines.append(f"STT_MODEL={config.stt_model}")
        if config.tts_api_key is not None:
            lines.append(f"TTS_API_KEY={config.tts_api_key}")
        lines.append("")
        
        # Memory Settings
        lines.append("# Memory Settings")
        lines.append(f"SUPABASE_URL={config.supabase_url}")
        lines.append(f"SUPABASE_KEY={config.supabase_key}")
        lines.append("")
        
        # API Keys for Skills
        lines.append("# API Keys for Skills")
        if config.brave_api_key is not None:
            lines.append(f"BRAVE_API_KEY={config.brave_api_key}")
        if config.google_calendar_credentials is not None:
            lines.append(f"GOOGLE_CALENDAR_CREDENTIALS={config.google_calendar_credentials}")
        if config.gmail_credentials is not None:
            lines.append(f"GMAIL_CREDENTIALS={config.gmail_credentials}")
        if config.home_assistant_url is not None:
            lines.append(f"HOME_ASSISTANT_URL={config.home_assistant_url}")
        if config.home_assistant_token is not None:
            lines.append(f"HOME_ASSISTANT_TOKEN={config.home_assistant_token}")
        if config.github_token is not None:
            lines.append(f"GITHUB_TOKEN={config.github_token}")
        if config.weather_api_key is not None:
            lines.append(f"WEATHER_API_KEY={config.weather_api_key}")
        lines.append("")
        
        # System Settings
        lines.append("# System Settings")
        lines.append(f"DASHBOARD_PORT={config.dashboard_port}")
        lines.append(f"JWT_SECRET={config.jwt_secret}")
        lines.append(f"LOG_LEVEL={config.log_level}")
        lines.append(f"LOG_DIR={config.log_dir}")
        lines.append(f"TIMEZONE={config.timezone}")
        
        return "\n".join(lines)
    
    @staticmethod
    def to_yaml_format(config: Configuration) -> str:
        """
        Convert a Configuration object to YAML format.
        
        Args:
            config: Configuration object to format
            
        Returns:
            String in YAML format
        """
        # Build a dictionary with all configuration values
        config_dict = {}
        
        # LLM Settings
        config_dict['llm_api_key'] = config.llm_api_key
        config_dict['llm_model'] = config.llm_model
        
        # Voice Settings
        config_dict['voice_enabled'] = config.voice_enabled
        config_dict['wake_word'] = config.wake_word
        config_dict['stt_model'] = config.stt_model
        if config.tts_api_key is not None:
            config_dict['tts_api_key'] = config.tts_api_key
        
        # Memory Settings
        config_dict['supabase_url'] = config.supabase_url
        config_dict['supabase_key'] = config.supabase_key
        
        # API Keys for Skills
        if config.brave_api_key is not None:
            config_dict['brave_api_key'] = config.brave_api_key
        if config.google_calendar_credentials is not None:
            config_dict['google_calendar_credentials'] = config.google_calendar_credentials
        if config.gmail_credentials is not None:
            config_dict['gmail_credentials'] = config.gmail_credentials
        if config.home_assistant_url is not None:
            config_dict['home_assistant_url'] = config.home_assistant_url
        if config.home_assistant_token is not None:
            config_dict['home_assistant_token'] = config.home_assistant_token
        if config.github_token is not None:
            config_dict['github_token'] = config.github_token
        if config.weather_api_key is not None:
            config_dict['weather_api_key'] = config.weather_api_key
        
        # System Settings
        config_dict['dashboard_port'] = config.dashboard_port
        config_dict['jwt_secret'] = config.jwt_secret
        config_dict['log_level'] = config.log_level
        config_dict['log_dir'] = config.log_dir
        config_dict['timezone'] = config.timezone
        
        # Convert to YAML format
        return yaml.dump(config_dict, default_flow_style=False, sort_keys=False)


def parse_config_file(file_path: Union[str, Path]) -> Configuration:
    """
    Parse a configuration file (.env or .yaml/.yml) into a Configuration object.
    
    Args:
        file_path: Path to the configuration file
        
    Returns:
        Configuration object with parsed values
        
    Raises:
        ConfigParseError: If file doesn't exist, is malformed, or validation fails
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise ConfigParseError(f"Configuration file not found: {file_path}")
    
    # Check if filename starts with .env or has .env extension
    if file_path.name.startswith('.env') or '.env' in file_path.name:
        return Config_Parser.parse_env_file(file_path)
    
    suffix = file_path.suffix.lower()
    if suffix in ('.yaml', '.yml'):
        return Config_Parser.parse_yaml_file(file_path)
    else:
        raise ConfigParseError(
            f"Unsupported configuration file format: {suffix}. "
            f"Supported formats: .env, .yaml, .yml"
        )


def format_config_to_env(config: Configuration) -> str:
    """
    Format a Configuration object to .env format.
    
    Args:
        config: Configuration object to format
        
    Returns:
        String in .env format
    """
    return Config_Formatter.to_env_format(config)


def format_config_to_yaml(config: Configuration) -> str:
    """
    Format a Configuration object to YAML format.
    
    Args:
        config: Configuration object to format
        
    Returns:
        String in YAML format
    """
    return Config_Formatter.to_yaml_format(config)
