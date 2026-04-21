"""Weather Information Skill for JARVIS using Weather API.

Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5
"""

import os
import time
import logging
from typing import Any, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import requests

from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class GetWeatherSkill(Skill):
    """
    Weather information skill that provides current conditions and 7-day forecast.
    
    Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5
    """
    
    def __init__(self):
        """Initialize the weather skill."""
        super().__init__()
        self._name = "get_weather"
        self._description = "Get current weather conditions and 7-day forecast for a location. If location is not specified, uses user's timezone from Personal Profile."
        self._parameters = {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location to get weather for (city name, zip code, or coordinates). Optional - will infer from user profile if not provided."
                }
            },
            "required": []  # location is optional per requirement 6.4
        }
        self._api_key = os.getenv("WEATHER_API_KEY")
        self._timeout = 2  # 2 seconds timeout as per requirement 6.5
    
    def execute(self, **kwargs) -> SkillResult:
        """
        Execute weather lookup with the provided location.
        
        Args:
            **kwargs: May contain 'location' parameter (optional)
            
        Returns:
            SkillResult with weather data or error message
            
        Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5
        """
        start_time = time.time()
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(**kwargs)
        if not is_valid:
            return SkillResult(
                success=False,
                result=None,
                error_message=error_msg,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        location = kwargs.get("location")
        
        # If location not provided, use default (requirement 6.4)
        # In a full implementation, this would query the Personal_Profile
        # For now, we'll require location or return an error
        if not location:
            return SkillResult(
                success=False,
                result=None,
                error_message="Location not specified and Personal Profile integration not yet implemented. Please provide a location.",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Check if API key is configured
        if not self._api_key or self._api_key == "your_weather_api_key_here":
            return SkillResult(
                success=False,
                result=None,
                error_message="Weather API key not configured. Please set WEATHER_API_KEY in .env file.",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        try:
            # Using WeatherAPI.com as the weather provider
            # Optimize by using forecast endpoint which includes current weather
            # This reduces 2 API calls to 1, improving performance
            forecast_url = "http://api.weatherapi.com/v1/forecast.json"
            forecast_params = {
                "key": self._api_key,
                "q": location,
                "days": 7,  # 7-day forecast as per requirement 6.3
                "aqi": "no",
                "alerts": "no"
            }
            
            # Single API call with timeout handling
            forecast_response = requests.get(
                forecast_url,
                params=forecast_params,
                timeout=self._timeout
            )
            
            if forecast_response.status_code != 200:
                error_msg = f"Weather API returned status code {forecast_response.status_code}"
                logger.warning(f"Weather API error for location '{location}': {error_msg}")
                return SkillResult(
                    success=False,
                    result=None,
                    error_message=f"{error_msg}: {forecast_response.text}",
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )
            
            forecast_data = forecast_response.json()
            current_data = forecast_data  # Current weather is included in forecast response
            
            # Format current conditions (requirement 6.2)
            current_conditions = {
                "location": current_data["location"]["name"],
                "region": current_data["location"]["region"],
                "country": current_data["location"]["country"],
                "temperature_f": current_data["current"]["temp_f"],
                "temperature_c": current_data["current"]["temp_c"],
                "condition": current_data["current"]["condition"]["text"],
                "humidity": current_data["current"]["humidity"],
                "wind_mph": current_data["current"]["wind_mph"],
                "wind_kph": current_data["current"]["wind_kph"],
                "feels_like_f": current_data["current"]["feelslike_f"],
                "feels_like_c": current_data["current"]["feelslike_c"],
                "last_updated": current_data["current"]["last_updated"]
            }
            
            # Format 7-day forecast (requirement 6.3)
            forecast_days = []
            for day in forecast_data["forecast"]["forecastday"]:
                forecast_days.append({
                    "date": day["date"],
                    "max_temp_f": day["day"]["maxtemp_f"],
                    "max_temp_c": day["day"]["maxtemp_c"],
                    "min_temp_f": day["day"]["mintemp_f"],
                    "min_temp_c": day["day"]["mintemp_c"],
                    "condition": day["day"]["condition"]["text"],
                    "chance_of_rain": day["day"]["daily_chance_of_rain"],
                    "chance_of_snow": day["day"]["daily_chance_of_snow"]
                })
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log performance metrics
            logger.info(f"Weather lookup completed for '{location}' in {execution_time}ms")
            
            # Warn if approaching timeout threshold (requirement 6.5: < 2s)
            if execution_time > 1500:
                logger.warning(f"Weather lookup for '{location}' took {execution_time}ms (approaching 2s limit)")
            
            return SkillResult(
                success=True,
                result={
                    "current": current_conditions,
                    "forecast": forecast_days
                },
                error_message=None,
                execution_time_ms=execution_time
            )
            
        except requests.exceptions.Timeout:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Weather lookup timed out after {self._timeout} seconds. Please try again."
            logger.error(f"Timeout error for location '{location}': {execution_time}ms")
            return SkillResult(
                success=False,
                result=None,
                error_message=error_msg,
                execution_time_ms=execution_time
            )
        except requests.exceptions.RequestException as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Network error during weather lookup: {str(e)}"
            logger.error(f"Network error for location '{location}': {error_msg}")
            return SkillResult(
                success=False,
                result=None,
                error_message=error_msg,
                execution_time_ms=execution_time
            )
        except KeyError as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Unexpected weather API response format: missing key {str(e)}"
            logger.error(f"API format error for location '{location}': {error_msg}")
            return SkillResult(
                success=False,
                result=None,
                error_message=error_msg,
                execution_time_ms=execution_time
            )
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Unexpected error during weather lookup: {str(e)}"
            logger.error(f"Unexpected error for location '{location}': {error_msg}")
            return SkillResult(
                success=False,
                result=None,
                error_message=error_msg,
                execution_time_ms=execution_time
            )
