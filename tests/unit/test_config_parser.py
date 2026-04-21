"""Unit tests for Config_Parser."""

import pytest
import tempfile
import os
import time
from pathlib import Path
from jarvis.config import Config_Parser, ConfigParseError, Configuration, parse_config_file


def create_temp_file(content: str, suffix: str):
    """Create a temporary file with content and return its path."""
    fd, path = tempfile.mkstemp(suffix=suffix, text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    except:
        os.close(fd)
        try:
            os.unlink(path)
        except:
            pass
        raise


def safe_unlink(path):
    """Safely unlink a file with retry logic for Windows."""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            os.unlink(path)
            return
        except PermissionError:
            if attempt < max_attempts - 1:
                time.sleep(0.1)
            else:
                # If we still can't delete, just pass - temp files will be cleaned up eventually
                pass


class TestConfigParserEnv:
    """Test Config_Parser with .env files."""
    
    def test_parse_valid_env_file(self):
        """Test parsing a valid .env file with all required fields."""
        content = """
# LLM Configuration
LLM_API_KEY=test_api_key_123
LLM_MODEL=claude-sonnet-4-20250514

# Memory Configuration
SUPABASE_URL=https://test.supabase.co
SUPABASE_KEY=test_supabase_key

# System Configuration
JWT_SECRET=test_jwt_secret_456
DASHBOARD_PORT=3000
LOG_LEVEL=INFO
"""
        temp_path = create_temp_file(content, '.env')
        
        try:
            config = Config_Parser.parse_env_file(temp_path)
            
            assert config.llm_api_key == "test_api_key_123"
            assert config.llm_model == "claude-sonnet-4-20250514"
            assert config.supabase_url == "https://test.supabase.co"
            assert config.supabase_key == "test_supabase_key"
            assert config.jwt_secret == "test_jwt_secret_456"
            assert config.dashboard_port == 3000
            assert config.log_level == "INFO"
        finally:
            safe_unlink(temp_path)
    
    def test_parse_env_file_with_quotes(self):
        """Test parsing .env file with quoted values."""
        content = """
LLM_API_KEY="quoted_key"
SUPABASE_URL='single_quoted_url'
SUPABASE_KEY=unquoted_key
JWT_SECRET="secret with spaces"
"""
        temp_path = create_temp_file(content, '.env')
        
        try:
            config = Config_Parser.parse_env_file(temp_path)
            
            assert config.llm_api_key == "quoted_key"
            assert config.supabase_url == "single_quoted_url"
            assert config.supabase_key == "unquoted_key"
            assert config.jwt_secret == "secret with spaces"
        finally:
            safe_unlink(temp_path)
    
    def test_parse_env_file_missing_required_field(self):
        """Test parsing .env file with missing required field."""
        content = """
LLM_API_KEY=test_key
SUPABASE_URL=https://test.supabase.co
# Missing SUPABASE_KEY and JWT_SECRET
"""
        temp_path = create_temp_file(content, '.env')
        
        try:
            with pytest.raises(ConfigParseError) as exc_info:
                Config_Parser.parse_env_file(temp_path)
            
            error_msg = str(exc_info.value)
            assert "Missing required field" in error_msg
            assert "supabase_key" in error_msg.lower() or "jwt_secret" in error_msg.lower()
        finally:
            safe_unlink(temp_path)
    
    def test_parse_env_file_invalid_type(self):
        """Test parsing .env file with invalid type for integer field."""
        content = """
LLM_API_KEY=test_key
SUPABASE_URL=https://test.supabase.co
SUPABASE_KEY=test_key
JWT_SECRET=test_secret
DASHBOARD_PORT=not_a_number
"""
        temp_path = create_temp_file(content, '.env')
        
        try:
            with pytest.raises(ConfigParseError) as exc_info:
                Config_Parser.parse_env_file(temp_path)
            
            error_msg = str(exc_info.value)
            assert "dashboard_port" in error_msg.lower()
            assert "integer" in error_msg.lower() or "int" in error_msg.lower()
        finally:
            safe_unlink(temp_path)
    
    def test_parse_env_file_invalid_boolean(self):
        """Test parsing .env file with invalid boolean value."""
        content = """
LLM_API_KEY=test_key
SUPABASE_URL=https://test.supabase.co
SUPABASE_KEY=test_key
JWT_SECRET=test_secret
VOICE_ENABLED=not_a_boolean
"""
        temp_path = create_temp_file(content, '.env')
        
        try:
            with pytest.raises(ConfigParseError) as exc_info:
                Config_Parser.parse_env_file(temp_path)
            
            error_msg = str(exc_info.value)
            assert "voice_enabled" in error_msg.lower()
            assert "bool" in error_msg.lower()
        finally:
            safe_unlink(temp_path)
    
    def test_parse_env_file_not_found(self):
        """Test parsing non-existent .env file."""
        with pytest.raises(ConfigParseError) as exc_info:
            Config_Parser.parse_env_file("nonexistent.env")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_parse_env_file_invalid_format(self):
        """Test parsing .env file with invalid format."""
        content = """
LLM_API_KEY=test_key
INVALID_LINE_WITHOUT_EQUALS
SUPABASE_URL=https://test.supabase.co
"""
        temp_path = create_temp_file(content, '.env')
        
        try:
            with pytest.raises(ConfigParseError) as exc_info:
                Config_Parser.parse_env_file(temp_path)
            
            error_msg = str(exc_info.value)
            assert "invalid format" in error_msg.lower()
            assert "KEY=VALUE" in error_msg
        finally:
            safe_unlink(temp_path)


class TestConfigParserYAML:
    """Test Config_Parser with YAML files."""
    
    def test_parse_valid_yaml_file(self):
        """Test parsing a valid YAML file with all required fields."""
        content = """
llm_api_key: test_api_key_123
llm_model: claude-sonnet-4-20250514
supabase_url: https://test.supabase.co
supabase_key: test_supabase_key
jwt_secret: test_jwt_secret_456
dashboard_port: 3000
log_level: INFO
voice_enabled: true
"""
        temp_path = create_temp_file(content, '.yaml')
        
        try:
            config = Config_Parser.parse_yaml_file(temp_path)
            
            assert config.llm_api_key == "test_api_key_123"
            assert config.llm_model == "claude-sonnet-4-20250514"
            assert config.supabase_url == "https://test.supabase.co"
            assert config.supabase_key == "test_supabase_key"
            assert config.jwt_secret == "test_jwt_secret_456"
            assert config.dashboard_port == 3000
            assert config.log_level == "INFO"
            assert config.voice_enabled is True
        finally:
            safe_unlink(temp_path)
    
    def test_parse_yaml_file_case_insensitive(self):
        """Test parsing YAML file with uppercase keys."""
        content = """
LLM_API_KEY: test_api_key_123
SUPABASE_URL: https://test.supabase.co
SUPABASE_KEY: test_supabase_key
JWT_SECRET: test_jwt_secret_456
"""
        temp_path = create_temp_file(content, '.yaml')
        
        try:
            config = Config_Parser.parse_yaml_file(temp_path)
            
            assert config.llm_api_key == "test_api_key_123"
            assert config.supabase_url == "https://test.supabase.co"
        finally:
            safe_unlink(temp_path)
    
    def test_parse_yaml_file_missing_required_field(self):
        """Test parsing YAML file with missing required field."""
        content = """
llm_api_key: test_key
supabase_url: https://test.supabase.co
# Missing supabase_key and jwt_secret
"""
        temp_path = create_temp_file(content, '.yaml')
        
        try:
            with pytest.raises(ConfigParseError) as exc_info:
                Config_Parser.parse_yaml_file(temp_path)
            
            error_msg = str(exc_info.value)
            assert "Missing required field" in error_msg
        finally:
            safe_unlink(temp_path)
    
    def test_parse_yaml_file_invalid_type(self):
        """Test parsing YAML file with invalid type."""
        content = """
llm_api_key: test_key
supabase_url: https://test.supabase.co
supabase_key: test_key
jwt_secret: test_secret
dashboard_port: "not_a_number"
"""
        temp_path = create_temp_file(content, '.yaml')
        
        try:
            with pytest.raises(ConfigParseError) as exc_info:
                Config_Parser.parse_yaml_file(temp_path)
            
            error_msg = str(exc_info.value)
            assert "dashboard_port" in error_msg.lower()
        finally:
            safe_unlink(temp_path)
    
    def test_parse_yaml_file_not_found(self):
        """Test parsing non-existent YAML file."""
        with pytest.raises(ConfigParseError) as exc_info:
            Config_Parser.parse_yaml_file("nonexistent.yaml")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_parse_yaml_file_invalid_syntax(self):
        """Test parsing YAML file with invalid syntax."""
        content = """
llm_api_key: test_key
  invalid_indentation: value
supabase_url: https://test.supabase.co
"""
        temp_path = create_temp_file(content, '.yaml')
        
        try:
            with pytest.raises(ConfigParseError) as exc_info:
                Config_Parser.parse_yaml_file(temp_path)
            
            error_msg = str(exc_info.value)
            assert "yaml" in error_msg.lower()
        finally:
            safe_unlink(temp_path)
    
    def test_parse_yaml_file_empty(self):
        """Test parsing empty YAML file."""
        content = ""
        temp_path = create_temp_file(content, '.yaml')
        
        try:
            with pytest.raises(ConfigParseError) as exc_info:
                Config_Parser.parse_yaml_file(temp_path)
            
            error_msg = str(exc_info.value)
            assert "empty" in error_msg.lower()
        finally:
            safe_unlink(temp_path)
    
    def test_parse_yaml_file_not_dict(self):
        """Test parsing YAML file that doesn't contain a dictionary."""
        content = "- item1\n- item2\n- item3"
        temp_path = create_temp_file(content, '.yaml')
        
        try:
            with pytest.raises(ConfigParseError) as exc_info:
                Config_Parser.parse_yaml_file(temp_path)
            
            error_msg = str(exc_info.value)
            assert "dictionary" in error_msg.lower()
        finally:
            safe_unlink(temp_path)


class TestParseConfigFile:
    """Test the parse_config_file convenience function."""
    
    def test_parse_config_file_env(self):
        """Test parse_config_file with .env file."""
        content = """
LLM_API_KEY=test_key
SUPABASE_URL=https://test.supabase.co
SUPABASE_KEY=test_key
JWT_SECRET=test_secret
"""
        temp_path = create_temp_file(content, '.env')
        
        try:
            config = parse_config_file(temp_path)
            assert config.llm_api_key == "test_key"
        finally:
            safe_unlink(temp_path)
    
    def test_parse_config_file_yaml(self):
        """Test parse_config_file with .yaml file."""
        content = """
llm_api_key: test_key
supabase_url: https://test.supabase.co
supabase_key: test_key
jwt_secret: test_secret
"""
        temp_path = create_temp_file(content, '.yaml')
        
        try:
            config = parse_config_file(temp_path)
            assert config.llm_api_key == "test_key"
        finally:
            safe_unlink(temp_path)
    
    def test_parse_config_file_yml(self):
        """Test parse_config_file with .yml file."""
        content = """
llm_api_key: test_key
supabase_url: https://test.supabase.co
supabase_key: test_key
jwt_secret: test_secret
"""
        temp_path = create_temp_file(content, '.yml')
        
        try:
            config = parse_config_file(temp_path)
            assert config.llm_api_key == "test_key"
        finally:
            safe_unlink(temp_path)
    
    def test_parse_config_file_unsupported_format(self):
        """Test parse_config_file with unsupported file format."""
        content = "some content"
        temp_path = create_temp_file(content, '.txt')
        
        try:
            with pytest.raises(ConfigParseError) as exc_info:
                parse_config_file(temp_path)
            
            error_msg = str(exc_info.value)
            assert "unsupported" in error_msg.lower()
            assert ".txt" in error_msg
        finally:
            safe_unlink(temp_path)
    
    def test_parse_config_file_not_found(self):
        """Test parse_config_file with non-existent file."""
        with pytest.raises(ConfigParseError) as exc_info:
            parse_config_file("nonexistent.yaml")
        
        assert "not found" in str(exc_info.value).lower()


class TestConfigParserEdgeCases:
    """Test edge cases for Config_Parser."""
    
    def test_parse_env_with_empty_lines_and_comments(self):
        """Test parsing .env file with empty lines and comments."""
        content = """
# This is a comment
LLM_API_KEY=test_key

# Another comment
SUPABASE_URL=https://test.supabase.co

SUPABASE_KEY=test_key
JWT_SECRET=test_secret
"""
        temp_path = create_temp_file(content, '.env')
        
        try:
            config = Config_Parser.parse_env_file(temp_path)
            assert config.llm_api_key == "test_key"
            assert config.supabase_url == "https://test.supabase.co"
        finally:
            safe_unlink(temp_path)
    
    def test_parse_env_with_equals_in_value(self):
        """Test parsing .env file with equals sign in value."""
        content = """
LLM_API_KEY=test_key
SUPABASE_URL=https://test.supabase.co?key=value
SUPABASE_KEY=test_key
JWT_SECRET=test_secret
"""
        temp_path = create_temp_file(content, '.env')
        
        try:
            config = Config_Parser.parse_env_file(temp_path)
            assert config.supabase_url == "https://test.supabase.co?key=value"
        finally:
            safe_unlink(temp_path)
    
    def test_parse_yaml_with_optional_fields(self):
        """Test parsing YAML with only required fields."""
        content = """
llm_api_key: test_key
supabase_url: https://test.supabase.co
supabase_key: test_key
jwt_secret: test_secret
"""
        temp_path = create_temp_file(content, '.yaml')
        
        try:
            config = Config_Parser.parse_yaml_file(temp_path)
            # Check required fields
            assert config.llm_api_key == "test_key"
            # Check optional fields have defaults
            assert config.llm_model == "claude-sonnet-4-20250514"
            assert config.voice_enabled is True
            assert config.dashboard_port == 3000
        finally:
            safe_unlink(temp_path)

