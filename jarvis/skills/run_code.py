"""Code Execution Skill for JARVIS with Docker-based sandbox.

Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
"""

import os
import time
import subprocess
import tempfile
from typing import Any, Dict, Optional
from pathlib import Path

from jarvis.skills.base import Skill, SkillResult


class RunCodeSkill(Skill):
    """
    Code execution skill that runs code in an isolated Docker sandbox.
    
    Supports Python, JavaScript, and Bash execution with 30-second timeout.
    Returns raw output and Brain-generated explanation.
    
    Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
    """
    
    def __init__(self):
        """Initialize the code execution skill."""
        super().__init__()
        self._name = "run_code"
        self._description = "Execute code snippets in Python, JavaScript, or Bash within an isolated sandbox environment. Returns raw output and explanation."
        self._parameters = {
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "Programming language to execute",
                    "enum": ["python", "javascript", "bash"]
                },
                "code": {
                    "type": "string",
                    "description": "The code to execute"
                }
            },
            "required": ["language", "code"]
        }
        self._timeout = 30  # 30-second timeout as per requirement 5.5
        
        # Docker image mappings for each language
        self._docker_images = {
            "python": "python:3.11-slim",
            "javascript": "node:18-slim",
            "bash": "bash:5.2"
        }
        
        # Command templates for each language
        self._command_templates = {
            "python": ["python", "-c"],
            "javascript": ["node", "-e"],
            "bash": ["bash", "-c"]
        }
    
    def _check_docker_available(self) -> tuple[bool, Optional[str]]:
        """
        Check if Docker is available and running.
        
        Returns:
            Tuple of (is_available, error_message)
        """
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, None
            else:
                return False, "Docker is not running or not accessible"
        except FileNotFoundError:
            return False, "Docker is not installed"
        except subprocess.TimeoutExpired:
            return False, "Docker command timed out"
        except Exception as e:
            return False, f"Error checking Docker: {str(e)}"
    
    def _execute_in_docker(
        self,
        language: str,
        code: str
    ) -> tuple[bool, str, str, int]:
        """
        Execute code in Docker container.
        
        Args:
            language: Programming language (python/javascript/bash)
            code: Code to execute
            
        Returns:
            Tuple of (success, stdout, stderr, exit_code)
        """
        docker_image = self._docker_images[language]
        command_template = self._command_templates[language]
        
        # Build docker run command
        docker_cmd = [
            "docker", "run",
            "--rm",  # Remove container after execution
            "--network", "none",  # No network access for security
            "--memory", "256m",  # Limit memory to 256MB
            "--cpus", "0.5",  # Limit CPU to 0.5 cores
            "--read-only",  # Read-only filesystem
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",  # Writable tmp with restrictions
            docker_image
        ] + command_template + [code]
        
        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                timeout=self._timeout,
                text=True
            )
            
            return (
                result.returncode == 0,
                result.stdout,
                result.stderr,
                result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return (
                False,
                "",
                f"Code execution timed out after {self._timeout} seconds",
                -1
            )
        except Exception as e:
            return (
                False,
                "",
                f"Error executing code in Docker: {str(e)}",
                -1
            )
    
    def _generate_explanation(
        self,
        language: str,
        code: str,
        stdout: str,
        stderr: str,
        exit_code: int
    ) -> str:
        """
        Generate a Brain-style explanation of the code execution.
        
        Args:
            language: Programming language
            code: Code that was executed
            stdout: Standard output
            stderr: Standard error
            exit_code: Exit code
            
        Returns:
            Human-readable explanation
        """
        if exit_code == 0:
            if stdout.strip():
                explanation = (
                    f"The {language} code executed successfully. "
                    f"It produced the following output:\n{stdout.strip()}"
                )
            else:
                explanation = (
                    f"The {language} code executed successfully with no output."
                )
        else:
            explanation = (
                f"The {language} code failed with exit code {exit_code}. "
            )
            if stderr.strip():
                explanation += f"Error details:\n{stderr.strip()}"
            else:
                explanation += "No error details were provided."
        
        return explanation
    
    def execute(self, **kwargs) -> SkillResult:
        """
        Execute code in an isolated Docker sandbox.
        
        Args:
            **kwargs: Must contain 'language' and 'code' parameters
            
        Returns:
            SkillResult with raw output and Brain-generated explanation
            
        Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
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
        
        language = kwargs.get("language")
        code = kwargs.get("code")
        
        # Validate language is supported (requirement 5.2)
        if language not in self._docker_images:
            return SkillResult(
                success=False,
                result=None,
                error_message=f"Unsupported language: {language}. Supported languages: python, javascript, bash",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Check if Docker is available (requirement 5.4)
        docker_available, docker_error = self._check_docker_available()
        if not docker_available:
            return SkillResult(
                success=False,
                result=None,
                error_message=f"Docker sandbox not available: {docker_error}",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Execute code in Docker sandbox (requirements 5.4, 5.5)
        success, stdout, stderr, exit_code = self._execute_in_docker(language, code)
        
        # Generate Brain explanation (requirement 5.3)
        explanation = self._generate_explanation(
            language, code, stdout, stderr, exit_code
        )
        
        execution_time = int((time.time() - start_time) * 1000)
        
        # Return both raw output and explanation (requirement 5.3)
        result_data = {
            "language": language,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "explanation": explanation
        }
        
        # If code execution failed, return error (requirement 5.6)
        if not success or exit_code != 0:
            return SkillResult(
                success=False,
                result=result_data,
                error_message=stderr if stderr else "Code execution failed",
                execution_time_ms=execution_time
            )
        
        return SkillResult(
            success=True,
            result=result_data,
            error_message=None,
            execution_time_ms=execution_time
        )
