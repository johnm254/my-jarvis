"""AgentSkills.io Standard Implementation

Implements the open standard for agent skills to ensure interoperability
with other frameworks like OpenJarvis, Hermes Agent, and OpenClaw.

Standard: https://agentskills.io/specification
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class SkillType(Enum):
    """Skill types following agentskills.io standard."""
    TOOL = "tool"  # External API or system call
    REASONING = "reasoning"  # Prompt-based reasoning pattern
    WORKFLOW = "workflow"  # Multi-step orchestration
    MEMORY = "memory"  # State management
    INTEGRATION = "integration"  # Third-party service


class SkillCategory(Enum):
    """Standard skill categories."""
    COMMUNICATION = "communication"  # Email, messaging, notifications
    PRODUCTIVITY = "productivity"  # Calendar, tasks, notes
    DEVELOPMENT = "development"  # Code, git, CI/CD
    RESEARCH = "research"  # Web search, document analysis
    AUTOMATION = "automation"  # Workflows, scheduling
    DATA = "data"  # Database, analytics
    SYSTEM = "system"  # OS operations, file management
    CREATIVE = "creative"  # Content generation, design
    PERSONAL = "personal"  # Health, finance, habits


@dataclass
class SkillSpec:
    """
    AgentSkills.io standard skill specification.
    
    This format ensures compatibility with:
    - OpenJarvis
    - Hermes Agent
    - OpenClaw
    - Any framework following agentskills.io
    """
    
    # Required fields
    name: str
    version: str
    description: str
    
    # Skill metadata
    type: SkillType
    category: SkillCategory
    author: str
    
    # Capabilities
    input_schema: Dict[str, Any]  # JSON Schema
    output_schema: Dict[str, Any]  # JSON Schema
    
    # Optional metadata with defaults
    license: str = "Apache-2.0"
    tags: List[str] = None
    examples: List[Dict[str, Any]] = None
    requires: List[str] = None  # Dependencies
    cost_estimate: str = None  # "free", "low", "medium", "high"
    latency_estimate: str = None  # "instant", "fast", "medium", "slow"
    
    # Source information
    source_url: Optional[str] = None
    documentation_url: Optional[str] = None
    
    def to_openjarvis_format(self) -> Dict[str, Any]:
        """Convert to OpenJarvis tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "metadata": {
                "version": self.version,
                "type": self.type.value,
                "category": self.category.value,
                "author": self.author,
                "tags": self.tags or [],
                "cost": self.cost_estimate,
                "latency": self.latency_estimate
            }
        }
    
    def to_claude_format(self) -> Dict[str, Any]:
        """Convert to Claude API tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillSpec':
        """Create SkillSpec from dictionary."""
        # Convert string enums to enum types
        if isinstance(data.get("type"), str):
            data["type"] = SkillType(data["type"])
        if isinstance(data.get("category"), str):
            data["category"] = SkillCategory(data["category"])
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "type": self.type.value,
            "category": self.category.value,
            "author": self.author,
            "license": self.license,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "tags": self.tags,
            "examples": self.examples,
            "requires": self.requires,
            "cost_estimate": self.cost_estimate,
            "latency_estimate": self.latency_estimate,
            "source_url": self.source_url,
            "documentation_url": self.documentation_url
        }


def create_skill_spec(
    name: str,
    description: str,
    input_schema: Dict[str, Any],
    output_schema: Dict[str, Any],
    category: SkillCategory,
    skill_type: SkillType = SkillType.TOOL,
    version: str = "1.0.0",
    author: str = "JARVIS",
    **kwargs
) -> SkillSpec:
    """Helper to create a skill specification."""
    return SkillSpec(
        name=name,
        version=version,
        description=description,
        type=skill_type,
        category=category,
        author=author,
        input_schema=input_schema,
        output_schema=output_schema,
        **kwargs
    )


# Example skill specifications following the standard
EXAMPLE_SKILLS = {
    "email_intake": SkillSpec(
        name="email_intake",
        version="1.0.0",
        description="Extract structured requirements from project emails using LLM parsing",
        type=SkillType.INTEGRATION,
        category=SkillCategory.COMMUNICATION,
        author="JARVIS",
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["poll", "parse"],
                    "description": "Poll inbox or parse email body"
                },
                "email_body": {
                    "type": "string",
                    "description": "Email text to parse"
                }
            },
            "required": ["action"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "project_name": {"type": "string"},
                "stack": {"type": "array", "items": {"type": "string"}},
                "features": {"type": "array", "items": {"type": "string"}},
                "deadline": {"type": "string"}
            }
        },
        tags=["email", "requirements", "parsing", "llm"],
        cost_estimate="low",
        latency_estimate="fast",
        requires=["gmail_api", "llm_api"]
    ),
    
    "project_architect": SkillSpec(
        name="project_architect",
        version="1.0.0",
        description="Generate project architecture including folder structure, ERD, API specs, and diagrams",
        type=SkillType.REASONING,
        category=SkillCategory.DEVELOPMENT,
        author="JARVIS",
        input_schema={
            "type": "object",
            "properties": {
                "spec_path": {
                    "type": "string",
                    "description": "Path to requirements JSON"
                }
            },
            "required": ["spec_path"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "folder_structure": {"type": "string"},
                "erd": {"type": "string"},
                "api_contract": {"type": "object"},
                "plan": {"type": "string"}
            }
        },
        tags=["architecture", "design", "planning", "diagrams"],
        cost_estimate="medium",
        latency_estimate="medium"
    ),
    
    "code_generator": SkillSpec(
        name="code_generator",
        version="1.0.0",
        description="Agentic code generation with iterative testing, linting, and auto-fixing",
        type=SkillType.WORKFLOW,
        category=SkillCategory.DEVELOPMENT,
        author="JARVIS",
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["generate", "test", "lint", "fix", "iterate"]
                },
                "plan_path": {"type": "string"},
                "max_iterations": {"type": "integer"}
            },
            "required": ["action"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "files_created": {"type": "array"},
                "test_passed": {"type": "boolean"},
                "iterations": {"type": "integer"}
            }
        },
        tags=["codegen", "testing", "linting", "automation"],
        cost_estimate="high",
        latency_estimate="slow",
        requires=["llm_api", "test_framework", "linter"]
    )
}
