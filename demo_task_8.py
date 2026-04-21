"""Demo script for Tasks 8.1, 8.2, and 8.3 - Skills Implementation.

This script demonstrates the three implemented skills:
- WebSearchSkill (Task 8.1)
- GetWeatherSkill (Task 8.2)
- SystemStatusSkill (Task 8.3)
"""

import json
from jarvis.skills import WebSearchSkill, GetWeatherSkill, SystemStatusSkill


def demo_web_search():
    """Demo the web_search skill."""
    print("=" * 80)
    print("TASK 8.1: WebSearchSkill Demo")
    print("=" * 80)
    
    skill = WebSearchSkill()
    print(f"Skill Name: {skill.name}")
    print(f"Description: {skill.description}")
    print(f"Parameters: {json.dumps(skill.parameters, indent=2)}")
    print()
    
    # Test with missing parameter
    print("Test 1: Missing required 'query' parameter")
    result = skill.execute()
    print(f"Success: {result.success}")
    print(f"Error: {result.error_message}")
    print()
    
    # Test with valid parameter (will fail without API key)
    print("Test 2: Valid parameter (requires API key)")
    result = skill.execute(query="Python programming")
    print(f"Success: {result.success}")
    print(f"Error: {result.error_message}")
    print(f"Execution time: {result.execution_time_ms}ms")
    print()


def demo_get_weather():
    """Demo the get_weather skill."""
    print("=" * 80)
    print("TASK 8.2: GetWeatherSkill Demo")
    print("=" * 80)
    
    skill = GetWeatherSkill()
    print(f"Skill Name: {skill.name}")
    print(f"Description: {skill.description}")
    print(f"Parameters: {json.dumps(skill.parameters, indent=2)}")
    print()
    
    # Test without location
    print("Test 1: No location provided")
    result = skill.execute()
    print(f"Success: {result.success}")
    print(f"Error: {result.error_message}")
    print()
    
    # Test with location (will fail without API key)
    print("Test 2: With location (requires API key)")
    result = skill.execute(location="Seattle")
    print(f"Success: {result.success}")
    print(f"Error: {result.error_message}")
    print(f"Execution time: {result.execution_time_ms}ms")
    print()


def demo_system_status():
    """Demo the system_status skill."""
    print("=" * 80)
    print("TASK 8.3: SystemStatusSkill Demo")
    print("=" * 80)
    
    skill = SystemStatusSkill()
    print(f"Skill Name: {skill.name}")
    print(f"Description: {skill.description}")
    print(f"Parameters: {json.dumps(skill.parameters, indent=2)}")
    print()
    
    # Test execution (should work without API keys)
    print("Test: Execute system status check")
    result = skill.execute()
    print(f"Success: {result.success}")
    print(f"Execution time: {result.execution_time_ms}ms")
    
    if result.success:
        print("\nSystem Status:")
        print(json.dumps(result.result, indent=2))
    else:
        print(f"Error: {result.error_message}")
    print()


if __name__ == "__main__":
    demo_web_search()
    demo_get_weather()
    demo_system_status()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✓ Task 8.1: WebSearchSkill implemented")
    print("  - Validates parameters (query required)")
    print("  - Integrates with Brave API")
    print("  - Returns top 3-5 search results")
    print("  - Handles timeout (3 seconds)")
    print("  - Returns error messages on failure")
    print()
    print("✓ Task 8.2: GetWeatherSkill implemented")
    print("  - Validates parameters (location optional)")
    print("  - Integrates with Weather API")
    print("  - Returns current conditions and 7-day forecast")
    print("  - Handles timeout (2 seconds)")
    print("  - Infers location from Personal Profile (placeholder)")
    print()
    print("✓ Task 8.3: SystemStatusSkill implemented")
    print("  - No parameters required")
    print("  - Uses psutil for system monitoring")
    print("  - Reports CPU usage percentage")
    print("  - Reports RAM usage in GB and percentage")
    print("  - Reports disk usage in GB and percentage")
    print("  - Lists top 5 processes by resource consumption")
    print()
