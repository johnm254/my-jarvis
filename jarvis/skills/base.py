"""Base Skill class and SkillRegistry for JARVIS."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import jsonschema
from jsonschema import validate, ValidationError


@dataclass
class SkillResult:
    """Result from skill execution."""
    success: bool
    result: Any
    error_message: Optional[str] = None
    execution_time_ms: int = 0


class Skill(ABC):
    """
    Base class for all JARVIS skills.
    
    Skills are executable tools that perform specific actions.
    Each skill defines its name, description, and parameter schema.
    
    Validates: Requirements 1.6, 1.7
    """
    
    def __init__(self):
        """Initialize the skill."""
        self._name: str = ""
        self._description: str = ""
        self._parameters: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        """Get the skill name."""
        return self._name
    
    @property
    def description(self) -> str:
        """Get the skill description."""
        return self._description
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """Get the skill parameter schema (JSON Schema format)."""
        return self._parameters
    
    def validate_parameters(self, **kwargs) -> tuple[bool, Optional[str]]:
        """
        Validate parameters against the skill's JSON schema.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Validates: Requirements 1.7
        """
        try:
            # Validate against JSON schema
            validate(instance=kwargs, schema=self._parameters)
            return True, None
        except ValidationError as e:
            # Return validation error message
            error_msg = f"Parameter validation failed: {e.message}"
            return False, error_msg
        except Exception as e:
            # Catch any other validation errors
            error_msg = f"Unexpected validation error: {str(e)}"
            return False, error_msg
    
    @abstractmethod
    def execute(self, **kwargs) -> SkillResult:
        """
        Execute the skill with provided parameters.
        
        Args:
            **kwargs: Skill parameters
            
        Returns:
            SkillResult with success status, result, and optional error message
        """
        pass


class SkillRegistry:
    """
    Registry for managing JARVIS skills.
    
    Provides methods to register, retrieve, and list skills.
    Converts skill definitions to Claude API tool format.
    
    Validates: Requirements 1.5, 1.6
    """
    
    def __init__(self):
        """Initialize the skill registry."""
        self._skills: Dict[str, Skill] = {}
    
    def register_skill(self, skill: Skill) -> None:
        """
        Register a skill in the registry.
        
        Args:
            skill: Skill instance to register
        """
        self._skills[skill.name] = skill
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """
        Retrieve a skill by name.
        
        Args:
            name: Skill name
            
        Returns:
            Skill instance or None if not found
        """
        return self._skills.get(name)
    
    def list_skills(self) -> List[Skill]:
        """
        List all registered skills.
        
        Returns:
            List of all registered skill instances
        """
        return list(self._skills.values())
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions in Claude API format.
        
        Converts all registered skills to Claude API tool format
        for use in LLM tool calling.
        
        Returns:
            List of tool definitions in Claude API format
        """
        tool_definitions = []
        
        for skill in self._skills.values():
            tool_def = {
                "name": skill.name,
                "description": skill.description,
                "input_schema": skill.parameters
            }
            tool_definitions.append(tool_def)
        
        return tool_definitions
