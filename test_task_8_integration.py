"""Integration test for Task 8 skills."""

from jarvis.skills import SkillRegistry, WebSearchSkill, GetWeatherSkill, SystemStatusSkill


def test_skill_registration():
    """Test that all three skills can be registered."""
    print("Creating skill registry...")
    registry = SkillRegistry()
    
    print("Registering skills...")
    registry.register_skill(WebSearchSkill())
    registry.register_skill(GetWeatherSkill())
    registry.register_skill(SystemStatusSkill())
    
    skills = registry.list_skills()
    print(f"✓ Successfully registered {len(skills)} skills")
    
    print("\nSkill Details:")
    for skill in skills:
        print(f"\n  {skill.name}:")
        print(f"    Description: {skill.description}")
        print(f"    Required params: {skill.parameters.get('required', [])}")
    
    # Test tool definitions
    tools = registry.get_tool_definitions()
    print(f"\n✓ Generated {len(tools)} tool definitions for Claude API")
    
    # Test skill retrieval
    web_search = registry.get_skill("web_search")
    get_weather = registry.get_skill("get_weather")
    system_status = registry.get_skill("system_status")
    
    assert web_search is not None, "web_search skill not found"
    assert get_weather is not None, "get_weather skill not found"
    assert system_status is not None, "system_status skill not found"
    
    print("\n✓ All skills can be retrieved by name")
    
    # Test system_status execution
    print("\nTesting system_status execution...")
    result = system_status.execute()
    assert result.success, f"system_status failed: {result.error_message}"
    assert result.result is not None, "system_status returned no result"
    assert "cpu" in result.result, "Missing CPU info"
    assert "ram" in result.result, "Missing RAM info"
    assert "disk" in result.result, "Missing disk info"
    assert "top_processes" in result.result, "Missing process info"
    
    print(f"✓ system_status executed successfully in {result.execution_time_ms}ms")
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED!")
    print("=" * 80)
    print("\n✓ Task 8.1: WebSearchSkill implemented")
    print("✓ Task 8.2: GetWeatherSkill implemented")
    print("✓ Task 8.3: SystemStatusSkill implemented")
    print("\nAll skills are ready for integration with the Brain!")


if __name__ == "__main__":
    test_skill_registration()
