"""Unit tests for skill performance optimizations.

Tests timeout handling and performance monitoring for web_search, get_weather, and github_summary skills.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from jarvis.skills.web_search import WebSearchSkill
from jarvis.skills.get_weather import GetWeatherSkill
from jarvis.skills.github_summary import GitHubSummarySkill


class TestWebSearchPerformance:
    """Test web_search skill performance optimizations."""
    
    def test_timeout_handling(self):
        """Test that web_search handles timeouts correctly."""
        skill = WebSearchSkill()
        skill._api_key = "test_api_key"  # Mock API key
        
        with patch('jarvis.skills.web_search.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()
            
            result = skill.execute(query="test query")
            
            assert result.success is False
            assert "timed out" in result.error_message.lower()
            assert result.execution_time_ms >= 0
    
    def test_performance_logging(self):
        """Test that web_search logs performance metrics."""
        skill = WebSearchSkill()
        skill._api_key = "test_api_key"  # Mock API key
        
        with patch('jarvis.skills.web_search.requests.get') as mock_get, \
             patch('jarvis.skills.web_search.logger') as mock_logger:
            
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "web": {
                    "results": [
                        {"title": "Test", "url": "http://test.com", "description": "Test result"}
                    ]
                }
            }
            mock_get.return_value = mock_response
            
            result = skill.execute(query="test query")
            
            assert result.success is True
            # Verify performance logging was called
            mock_logger.info.assert_called()
            assert "completed" in str(mock_logger.info.call_args)


class TestGetWeatherPerformance:
    """Test get_weather skill performance optimizations."""
    
    def test_single_api_call_optimization(self):
        """Test that get_weather uses single API call instead of two."""
        skill = GetWeatherSkill()
        skill._api_key = "test_api_key"  # Mock API key
        
        with patch('jarvis.skills.get_weather.requests.get') as mock_get:
            # Mock successful response with both current and forecast data
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "location": {
                    "name": "Seattle",
                    "region": "Washington",
                    "country": "USA"
                },
                "current": {
                    "temp_f": 65.0,
                    "temp_c": 18.3,
                    "condition": {"text": "Partly cloudy"},
                    "humidity": 70,
                    "wind_mph": 10.0,
                    "wind_kph": 16.1,
                    "feelslike_f": 63.0,
                    "feelslike_c": 17.2,
                    "last_updated": "2024-01-15 12:00"
                },
                "forecast": {
                    "forecastday": [
                        {
                            "date": "2024-01-15",
                            "day": {
                                "maxtemp_f": 70.0,
                                "maxtemp_c": 21.1,
                                "mintemp_f": 55.0,
                                "mintemp_c": 12.8,
                                "condition": {"text": "Sunny"},
                                "daily_chance_of_rain": 10,
                                "daily_chance_of_snow": 0
                            }
                        }
                    ]
                }
            }
            mock_get.return_value = mock_response
            
            result = skill.execute(location="Seattle")
            
            # Verify only one API call was made (optimization)
            assert mock_get.call_count == 1
            assert result.success is True
    
    def test_timeout_handling(self):
        """Test that get_weather handles timeouts correctly."""
        skill = GetWeatherSkill()
        skill._api_key = "test_api_key"  # Mock API key
        
        with patch('jarvis.skills.get_weather.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()
            
            result = skill.execute(location="Seattle")
            
            assert result.success is False
            assert "timed out" in result.error_message.lower()
            assert result.execution_time_ms >= 0
    
    def test_performance_logging(self):
        """Test that get_weather logs performance metrics."""
        skill = GetWeatherSkill()
        skill._api_key = "test_api_key"  # Mock API key
        
        with patch('jarvis.skills.get_weather.requests.get') as mock_get, \
             patch('jarvis.skills.get_weather.logger') as mock_logger:
            
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "location": {"name": "Seattle", "region": "WA", "country": "USA"},
                "current": {
                    "temp_f": 65.0, "temp_c": 18.3,
                    "condition": {"text": "Cloudy"},
                    "humidity": 70, "wind_mph": 10.0, "wind_kph": 16.1,
                    "feelslike_f": 63.0, "feelslike_c": 17.2,
                    "last_updated": "2024-01-15 12:00"
                },
                "forecast": {"forecastday": []}
            }
            mock_get.return_value = mock_response
            
            result = skill.execute(location="Seattle")
            
            assert result.success is True
            # Verify performance logging was called
            mock_logger.info.assert_called()


class TestGitHubSummaryPerformance:
    """Test github_summary skill performance optimizations."""
    
    def test_parallel_api_calls(self):
        """Test that github_summary makes parallel API calls."""
        skill = GitHubSummarySkill()
        skill._github_token = "test_token"  # Mock GitHub token
        
        with patch('jarvis.skills.github_summary.requests.get') as mock_get:
            # Mock successful responses
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            result = skill.execute(repo="facebook/react")
            
            # Verify multiple API calls were made (PRs, issues, commits)
            assert mock_get.call_count == 3
            assert result.success is True
    
    def test_partial_failure_handling(self):
        """Test that github_summary handles partial failures gracefully."""
        skill = GitHubSummarySkill()
        skill._github_token = "test_token"  # Mock GitHub token
        
        with patch('jarvis.skills.github_summary.requests.get') as mock_get:
            # Mock one successful and one failed response
            responses = []
            
            # First call succeeds (PRs)
            success_response = Mock()
            success_response.status_code = 200
            success_response.json.return_value = []
            responses.append(success_response)
            
            # Second call fails (issues)
            fail_response = Mock()
            fail_response.status_code = 500
            fail_response.text = "Internal Server Error"
            responses.append(fail_response)
            
            # Third call succeeds (commits)
            responses.append(success_response)
            
            mock_get.side_effect = responses
            
            result = skill.execute(repo="facebook/react")
            
            # Should still succeed with partial data
            assert result.success is True
            assert result.result.get("partial_failures") is not None
    
    def test_timeout_handling(self):
        """Test that github_summary handles timeouts correctly."""
        skill = GitHubSummarySkill()
        skill._github_token = "test_token"  # Mock GitHub token
        
        with patch('jarvis.skills.github_summary.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()
            
            result = skill.execute(repo="facebook/react")
            
            # Should fail if all requests timeout
            assert result.success is False
            assert "timed out" in result.error_message.lower() or "failed" in result.error_message.lower()
    
    def test_performance_logging(self):
        """Test that github_summary logs performance metrics."""
        skill = GitHubSummarySkill()
        skill._github_token = "test_token"  # Mock GitHub token
        
        with patch('jarvis.skills.github_summary.requests.get') as mock_get, \
             patch('jarvis.skills.github_summary.logger') as mock_logger:
            
            # Mock successful responses
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            result = skill.execute(repo="facebook/react")
            
            assert result.success is True
            # Verify performance logging was called
            mock_logger.info.assert_called()
            assert "completed" in str(mock_logger.info.call_args)
