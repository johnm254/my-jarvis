"""Daily Brief Skill for JARVIS - orchestrates multiple skills.

Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5
"""

import time
from typing import Any, Dict, Optional

from jarvis.skills.base import Skill, SkillResult


class DailyBriefSkill(Skill):
    """
    Daily brief skill that orchestrates multiple skills to provide a morning summary.
    
    Aggregates weather, calendar events, email summary, and news headlines.
    Generates a cohesive spoken summary optimized for TTS delivery.
    
    Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5
    """
    
    def __init__(self, skill_registry=None):
        """
        Initialize the daily brief skill.
        
        Args:
            skill_registry: SkillRegistry instance for calling other skills
        """
        super().__init__()
        self._name = "daily_brief"
        self._description = "Generate a comprehensive daily brief including weather, calendar events, email summary, and news headlines. Optimized for spoken delivery."
        self._parameters = {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Location for weather forecast (optional, will use user profile if not provided)"
                },
                "news_query": {
                    "type": "string",
                    "description": "Search query for news headlines (optional, defaults to 'top news today')"
                }
            },
            "required": []  # No required parameters per requirement 11.1
        }
        
        self._skill_registry = skill_registry
    
    def _get_weather(self, location: Optional[str] = None) -> tuple[bool, str, Optional[str]]:
        """
        Get weather information.
        
        Args:
            location: Optional location for weather
            
        Returns:
            Tuple of (success, weather_summary, error_message)
        """
        if not self._skill_registry:
            return False, "", "Skill registry not available"
        
        weather_skill = self._skill_registry.get_skill("get_weather")
        if not weather_skill:
            return False, "", "Weather skill not available"
        
        # Call weather skill
        params = {}
        if location:
            params["location"] = location
        
        result = weather_skill.execute(**params)
        
        if not result.success:
            return False, "", result.error_message or "Weather lookup failed"
        
        # Format weather for spoken delivery
        weather_data = result.result
        current = weather_data.get("current", {})
        forecast = weather_data.get("forecast", [])
        
        summary_parts = []
        
        # Current weather
        if current:
            temp_f = current.get("temperature_f")
            condition = current.get("condition")
            location_name = current.get("location")
            summary_parts.append(
                f"Currently in {location_name}, it's {temp_f} degrees and {condition.lower()}."
            )
        
        # Today's forecast
        if forecast and len(forecast) > 0:
            today = forecast[0]
            high = today.get("max_temp_f")
            low = today.get("min_temp_f")
            condition = today.get("condition")
            rain_chance = today.get("chance_of_rain")
            
            summary_parts.append(
                f"Today's high will be {high} degrees with a low of {low}. "
                f"Expect {condition.lower()}"
            )
            
            if rain_chance and int(rain_chance) > 30:
                summary_parts.append(f"with a {rain_chance}% chance of rain")
        
        return True, " ".join(summary_parts), None
    
    def _get_calendar_events(self) -> tuple[bool, str, Optional[str]]:
        """
        Get calendar events for today.
        
        Returns:
            Tuple of (success, calendar_summary, error_message)
        """
        if not self._skill_registry:
            return False, "", "Skill registry not available"
        
        calendar_skill = self._skill_registry.get_skill("manage_calendar")
        if not calendar_skill:
            return False, "", "Calendar skill not available"
        
        # Call calendar skill to read today's events
        result = calendar_skill.execute(
            action="read",
            details={"days_ahead": 1}
        )
        
        if not result.success:
            # Calendar might not be configured - that's okay
            return True, "No calendar events scheduled for today.", None
        
        # Format calendar events for spoken delivery
        events = result.result.get("events", [])
        
        if not events:
            return True, "You have no calendar events scheduled for today.", None
        
        summary_parts = [f"You have {len(events)} event{'s' if len(events) != 1 else ''} today:"]
        
        for event in events[:5]:  # Limit to first 5 events
            title = event.get("title", "Untitled event")
            start_time = event.get("start_time", "")
            summary_parts.append(f"{title} at {start_time}")
        
        if len(events) > 5:
            summary_parts.append(f"and {len(events) - 5} more events")
        
        return True, " ".join(summary_parts), None
    
    def _get_email_summary(self) -> tuple[bool, str, Optional[str]]:
        """
        Get email summary.
        
        Returns:
            Tuple of (success, email_summary, error_message)
        """
        if not self._skill_registry:
            return False, "", "Skill registry not available"
        
        email_skill = self._skill_registry.get_skill("manage_email")
        if not email_skill:
            return False, "", "Email skill not available"
        
        # Call email skill to summarize unread emails
        result = email_skill.execute(
            action="summarize",
            filters={"label": "UNREAD"}
        )
        
        if not result.success:
            # Email might not be configured - that's okay
            return True, "No unread emails.", None
        
        # Format email summary for spoken delivery
        email_data = result.result
        unread_count = email_data.get("unread_count", 0)
        summary = email_data.get("summary", "")
        
        if unread_count == 0:
            return True, "You have no unread emails.", None
        
        return True, f"You have {unread_count} unread email{'s' if unread_count != 1 else ''}. {summary}", None
    
    def _get_news_headlines(self, query: Optional[str] = None) -> tuple[bool, str, Optional[str]]:
        """
        Get news headlines.
        
        Args:
            query: Optional search query for news
            
        Returns:
            Tuple of (success, news_summary, error_message)
        """
        if not self._skill_registry:
            return False, "", "Skill registry not available"
        
        search_skill = self._skill_registry.get_skill("web_search")
        if not search_skill:
            return False, "", "Web search skill not available"
        
        # Call web search skill for news
        search_query = query or "top news today"
        result = search_skill.execute(query=search_query)
        
        if not result.success:
            return False, "", result.error_message or "News search failed"
        
        # Format news headlines for spoken delivery
        search_results = result.result.get("results", [])
        
        if not search_results:
            return True, "No news headlines available.", None
        
        summary_parts = ["Here are today's top headlines:"]
        
        for i, article in enumerate(search_results[:3], 1):  # Top 3 headlines
            title = article.get("title", "")
            summary_parts.append(f"{i}. {title}")
        
        return True, " ".join(summary_parts), None
    
    def _generate_cohesive_summary(
        self,
        weather: str,
        calendar: str,
        email: str,
        news: str
    ) -> str:
        """
        Generate a cohesive spoken summary from all components.
        
        Args:
            weather: Weather summary
            calendar: Calendar summary
            email: Email summary
            news: News summary
            
        Returns:
            Cohesive summary optimized for TTS
        """
        # Build summary with natural pacing for TTS (requirement 11.5)
        summary_parts = []
        
        # Greeting
        summary_parts.append("Good morning, Boss. Here's your daily brief.")
        summary_parts.append("")  # Pause
        
        # Weather section
        if weather:
            summary_parts.append(weather)
            summary_parts.append("")  # Pause
        
        # Calendar section
        if calendar:
            summary_parts.append(calendar)
            summary_parts.append("")  # Pause
        
        # Email section
        if email:
            summary_parts.append(email)
            summary_parts.append("")  # Pause
        
        # News section
        if news:
            summary_parts.append(news)
        
        # Closing
        summary_parts.append("")  # Pause
        summary_parts.append("That's your brief for today. Have a great day!")
        
        return "\n".join(summary_parts)
    
    def execute(self, **kwargs) -> SkillResult:
        """
        Execute daily brief generation.
        
        Args:
            **kwargs: Optional 'location' and 'news_query' parameters
            
        Returns:
            SkillResult with daily brief summary
            
        Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5
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
        news_query = kwargs.get("news_query")
        
        # Check if skill registry is available
        if not self._skill_registry:
            return SkillResult(
                success=False,
                result=None,
                error_message="Skill registry not initialized. Cannot orchestrate other skills.",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Aggregate data from all sources (requirement 11.2)
        errors = []
        
        # Get weather (requirement 11.3)
        weather_success, weather_summary, weather_error = self._get_weather(location)
        if not weather_success:
            errors.append(f"Weather: {weather_error}")
            weather_summary = ""
        
        # Get calendar events (requirement 11.3)
        calendar_success, calendar_summary, calendar_error = self._get_calendar_events()
        if not calendar_success:
            errors.append(f"Calendar: {calendar_error}")
            calendar_summary = ""
        
        # Get email summary (requirement 11.3)
        email_success, email_summary, email_error = self._get_email_summary()
        if not email_success:
            errors.append(f"Email: {email_error}")
            email_summary = ""
        
        # Get news headlines (requirement 11.3)
        news_success, news_summary, news_error = self._get_news_headlines(news_query)
        if not news_success:
            errors.append(f"News: {news_error}")
            news_summary = ""
        
        # Generate cohesive summary (requirements 11.4, 11.5)
        cohesive_summary = self._generate_cohesive_summary(
            weather_summary,
            calendar_summary,
            email_summary,
            news_summary
        )
        
        execution_time = int((time.time() - start_time) * 1000)
        
        result = {
            "summary": cohesive_summary,
            "components": {
                "weather": weather_summary,
                "calendar": calendar_summary,
                "email": email_summary,
                "news": news_summary
            },
            "errors": errors if errors else None
        }
        
        # If all components failed, return error
        if not any([weather_success, calendar_success, email_success, news_success]):
            return SkillResult(
                success=False,
                result=result,
                error_message="All data sources failed. " + "; ".join(errors),
                execution_time_ms=execution_time
            )
        
        return SkillResult(
            success=True,
            result=result,
            error_message=None,
            execution_time_ms=execution_time
        )
