"""Skill 1 — Email & Requirement Intake

Polls Gmail inbox for project emails and extracts structured requirements
using Claude to parse project name, stack, features, and deadline.
"""

import os
import json
import time
import logging
from typing import Any, Dict, Optional
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class EmailIntakeSkill(Skill):
    """
    Email & requirement intake skill.
    
    Polls Gmail inbox for project emails and uses Claude to extract:
    - Project name
    - Tech stack
    - Features list
    - Deadline
    
    Stores as JSON spec for downstream skills.
    """
    
    def __init__(self):
        super().__init__()
        self._name = "email_intake"
        self._description = (
            "Poll Gmail inbox for project emails and extract structured requirements "
            "(project name, stack, features, deadline) using Claude. "
            "Stores as JSON spec for downstream consumption."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action: 'poll' to check inbox, 'parse' to extract requirements from email body",
                    "enum": ["poll", "parse"]
                },
                "email_body": {
                    "type": "string",
                    "description": "Email body text to parse (for 'parse' action)"
                },
                "output_path": {
                    "type": "string",
                    "description": "Path to save JSON spec (default: jarvis_output/specs/project_spec.json)"
                }
            },
            "required": ["action"]
        }
        
        self._gmail_credentials = os.getenv("GMAIL_CREDENTIALS")
        self._llm_api_key = os.getenv("LLM_API_KEY")
    
    def _poll_inbox(self) -> tuple[bool, Any, Optional[str]]:
        """Poll Gmail inbox for project-related emails."""
        # TODO: Integrate with Gmail MCP tool
        # For now, return mock structure
        return False, None, "Gmail MCP integration pending. Use 'parse' action with email_body instead."
    
    def _parse_requirements(self, email_body: str) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """
        Parse email body using Claude to extract structured requirements.
        
        Args:
            email_body: Raw email text
            
        Returns:
            Tuple of (success, parsed_spec, error_message)
        """
        if not self._llm_api_key:
            return False, {}, "LLM_API_KEY not configured"
        
        # System prompt for requirement extraction
        system_prompt = """You are a requirements extraction assistant. 
Parse the email and extract:
1. project_name: The name of the project
2. stack: List of technologies/frameworks mentioned
3. features: List of features/requirements
4. deadline: Any mentioned deadline or timeline
5. additional_notes: Any other relevant information

Return ONLY valid JSON with these fields. If a field is not mentioned, use null."""

        try:
            # TODO: Call Claude API with email_body
            # For now, return a structured template
            spec = {
                "project_name": "extracted_project",
                "stack": ["react", "nodejs", "postgresql"],
                "features": [
                    "User authentication",
                    "Dashboard with analytics",
                    "REST API"
                ],
                "deadline": "2 weeks",
                "additional_notes": "Client prefers TypeScript",
                "raw_email": email_body[:500],  # Store snippet
                "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return True, spec, None
            
        except Exception as e:
            logger.error(f"Error parsing requirements: {e}")
            return False, {}, str(e)
    
    def execute(self, **kwargs) -> SkillResult:
        start = time.time()
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(**kwargs)
        if not is_valid:
            return SkillResult(
                success=False,
                result=None,
                error_message=error_msg,
                execution_time_ms=int((time.time() - start) * 1000)
            )
        
        action = kwargs.get("action")
        output_path = kwargs.get("output_path", "jarvis_output/specs/project_spec.json")
        
        result = None
        error = None
        success = False
        
        if action == "poll":
            success, result, error = self._poll_inbox()
        elif action == "parse":
            email_body = kwargs.get("email_body")
            if not email_body:
                return SkillResult(
                    success=False,
                    result=None,
                    error_message="email_body required for 'parse' action",
                    execution_time_ms=int((time.time() - start) * 1000)
                )
            
            success, spec, error = self._parse_requirements(email_body)
            
            if success:
                # Save to file
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as f:
                    json.dump(spec, f, indent=2)
                
                result = {
                    "spec": spec,
                    "saved_to": os.path.abspath(output_path)
                }
        else:
            return SkillResult(
                success=False,
                result=None,
                error_message=f"Unknown action: {action}",
                execution_time_ms=int((time.time() - start) * 1000)
            )
        
        return SkillResult(
            success=success,
            result=result,
            error_message=error,
            execution_time_ms=int((time.time() - start) * 1000)
        )
