"""Demonstration of Task 5.5: execute_tool_call() implementation."""

from jarvis.brain import Brain, ToolResult
from jarvis.skills import Skill, SkillRegistry, SkillResult


class EchoSkill(Skill):
    """Simple echo skill for demonstration."""
    
    def __init__(self):
        super().__init__()
        self._name = "echo"
        self._description = "Echoes back the input message"
        self._parameters = {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message to echo back"
                },
                "repeat": {
                    "type": "integer",
                    "description": "Number of times to repeat",
                    "minimum": 1,
                    "maximum": 5
                }
            },
            "required": ["message"]
        }
    
    def execute(self, **kwargs) -> SkillResult:
        """Execute the echo skill."""
        message = kwargs.get("message", "")
        repeat = kwargs.get("repeat", 1)
        
        result = " ".join([message] * repeat)
        
        return SkillResult(
            success=True,
            result=result,
            error_message=None,
            execution_time_ms=5
        )


def main():
    """Demonstrate execute_tool_call() functionality."""
    print("=" * 70)
    print("Task 5.5 Demonstration: execute_tool_call() with Validation")
    print("=" * 70)
    print()
    
    # Create minimal config for demo
    config = type('Config', (), {
        'llm_api_key': 'demo_key',
        'llm_model': 'claude-sonnet-4-20250514'
    })()
    
    # Create skill registry and register echo skill
    registry = SkillRegistry()
    echo_skill = EchoSkill()
    registry.register_skill(echo_skill)
    
    print(f"✓ Registered skill: {echo_skill.name}")
    print(f"  Description: {echo_skill.description}")
    print()
    
    # Create Brain with skill registry
    brain = Brain(config, skill_registry=registry)
    print("✓ Created Brain with skill registry")
    print()
    
    # Demo 1: Valid call with required parameter only
    print("Demo 1: Valid call with required parameter")
    print("-" * 70)
    result = brain.execute_tool_call("echo", {"message": "Hello, JARVIS!"})
    print(f"Tool: echo")
    print(f"Parameters: {{'message': 'Hello, JARVIS!'}}")
    print(f"Success: {result.success}")
    print(f"Result: {result.result}")
    print(f"Execution time: {result.execution_time_ms}ms")
    print()
    
    # Demo 2: Valid call with optional parameter
    print("Demo 2: Valid call with optional parameter")
    print("-" * 70)
    result = brain.execute_tool_call("echo", {"message": "JARVIS", "repeat": 3})
    print(f"Tool: echo")
    print(f"Parameters: {{'message': 'JARVIS', 'repeat': 3}}")
    print(f"Success: {result.success}")
    print(f"Result: {result.result}")
    print(f"Execution time: {result.execution_time_ms}ms")
    print()
    
    # Demo 3: Invalid call - missing required parameter
    print("Demo 3: Invalid call - missing required parameter")
    print("-" * 70)
    result = brain.execute_tool_call("echo", {"repeat": 2})
    print(f"Tool: echo")
    print(f"Parameters: {{'repeat': 2}}")
    print(f"Success: {result.success}")
    print(f"Result: {result.result}")
    print(f"Error: {result.error_message}")
    print(f"Execution time: {result.execution_time_ms}ms")
    print()
    
    # Demo 4: Invalid call - wrong parameter type
    print("Demo 4: Invalid call - wrong parameter type")
    print("-" * 70)
    result = brain.execute_tool_call("echo", {"message": "test", "repeat": "three"})
    print(f"Tool: echo")
    print(f"Parameters: {{'message': 'test', 'repeat': 'three'}}")
    print(f"Success: {result.success}")
    print(f"Result: {result.result}")
    print(f"Error: {result.error_message}")
    print(f"Execution time: {result.execution_time_ms}ms")
    print()
    
    # Demo 5: Non-existent skill
    print("Demo 5: Non-existent skill")
    print("-" * 70)
    result = brain.execute_tool_call("nonexistent", {"param": "value"})
    print(f"Tool: nonexistent")
    print(f"Parameters: {{'param': 'value'}}")
    print(f"Success: {result.success}")
    print(f"Result: {result.result}")
    print(f"Error: {result.error_message}")
    print(f"Execution time: {result.execution_time_ms}ms")
    print()
    
    print("=" * 70)
    print("Key Features Demonstrated:")
    print("=" * 70)
    print("✓ Parameter validation against JSON Schema")
    print("✓ Required vs optional parameter handling")
    print("✓ Type validation (string, integer)")
    print("✓ Execution time tracking")
    print("✓ Comprehensive error messages")
    print("✓ Skill registry integration")
    print()
    print("Requirements Validated:")
    print("✓ Requirement 1.6: Tool call architecture")
    print("✓ Requirement 1.7: Parameter validation before invocation")


if __name__ == "__main__":
    main()
