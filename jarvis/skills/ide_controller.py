"""Skill 5 — IDE & Local Environment Control

Controls local development environment:
- Open projects in VS Code
- Run package installations (npm/pip)
- Start dev servers
- Tail logs
- Execute shell commands
"""

import os
import time
import subprocess
import logging
from typing import Any, Dict, Optional
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class IDEControllerSkill(Skill):
    """
    IDE & local environment control skill.
    
    Features:
    - Open projects in VS Code
    - Run npm install / pip install
    - Start dev servers
    - Tail logs
    - Execute shell commands
    - System automation (platform-specific)
    """
    
    def __init__(self):
        super().__init__()
        self._name = "ide_controller"
        self._description = (
            "Control local development environment: "
            "open VS Code, install packages, start dev servers, tail logs."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action: 'open_vscode', 'npm_install', 'pip_install', 'start_server', 'tail_log', 'run_shell'",
                    "enum": ["open_vscode", "npm_install", "pip_install", "start_server", "tail_log", "run_shell"]
                },
                "project_dir": {
                    "type": "string",
                    "description": "Project directory path"
                },
                "package": {
                    "type": "string",
                    "description": "Package name to install (for npm_install, pip_install)"
                },
                "script": {
                    "type": "string",
                    "description": "Script name to run (for start_server, e.g., 'dev', 'start')"
                },
                "log_file": {
                    "type": "string",
                    "description": "Log file path (for tail_log)"
                },
                "command": {
                    "type": "string",
                    "description": "Shell command to execute (for run_shell)"
                },
                "lines": {
                    "type": "integer",
                    "description": "Number of log lines to tail (default: 50)"
                }
            },
            "required": ["action"]
        }
    
    def _run_command(self, cmd: str, cwd: str = None, timeout: int = 60, background: bool = False) -> Dict[str, Any]:
        """Run shell command and return result."""
        try:
            if background:
                # Start process in background
                subprocess.Popen(cmd, shell=True, cwd=cwd or os.getcwd())
                return {
                    "stdout": f"Started in background: {cmd}",
                    "stderr": "",
                    "returncode": 0,
                    "success": True
                }
            else:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True,
                    cwd=cwd or os.getcwd(), timeout=timeout
                )
                return {
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip(),
                    "returncode": result.returncode,
                    "success": result.returncode == 0
                }
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": "Command timed out", "returncode": -1, "success": False}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": -1, "success": False}
    
    def _open_vscode(self, project_dir: str) -> tuple[bool, str, Optional[str]]:
        """Open project in VS Code."""
        if not os.path.exists(project_dir):
            return False, "", f"Project directory not found: {project_dir}"
        
        # Use 'code' command to open VS Code
        result = self._run_command(f'code "{project_dir}"', background=True)
        
        if result["success"]:
            return True, f"Opened {project_dir} in VS Code", None
        else:
            return False, "", f"Failed to open VS Code: {result['stderr']}"
    
    def _npm_install(self, project_dir: str, package: str = None) -> tuple[bool, str, Optional[str]]:
        """Run npm install."""
        if package:
            cmd = f"npm install {package}"
        else:
            cmd = "npm install"
        
        result = self._run_command(cmd, cwd=project_dir, timeout=180)
        
        if result["success"]:
            return True, f"Installed: {package or 'all dependencies'}", None
        else:
            return False, "", f"npm install failed: {result['stderr']}"
    
    def _pip_install(self, project_dir: str, package: str = None) -> tuple[bool, str, Optional[str]]:
        """Run pip install."""
        if not package:
            # Install from requirements.txt
            if os.path.exists(os.path.join(project_dir, "requirements.txt")):
                cmd = "pip install -r requirements.txt"
            else:
                return False, "", "No package specified and requirements.txt not found"
        else:
            cmd = f"pip install {package}"
        
        result = self._run_command(cmd, cwd=project_dir, timeout=180)
        
        if result["success"]:
            return True, f"Installed: {package or 'requirements.txt'}", None
        else:
            return False, "", f"pip install failed: {result['stderr']}"
    
    def _start_server(self, project_dir: str, script: str = "dev") -> tuple[bool, str, Optional[str]]:
        """Start development server in background."""
        # Detect project type
        if os.path.exists(os.path.join(project_dir, "package.json")):
            cmd = f"npm run {script}"
        elif os.path.exists(os.path.join(project_dir, "manage.py")):
            # Django
            cmd = "python manage.py runserver"
        elif os.path.exists(os.path.join(project_dir, "main.py")):
            # FastAPI or generic Python
            cmd = "uvicorn main:app --reload"
        else:
            return False, "", "Could not detect project type"
        
        result = self._run_command(cmd, cwd=project_dir, background=True)
        
        return True, f"Started server: {cmd}", None
    
    def _tail_log(self, log_file: str, lines: int = 50) -> tuple[bool, str, Optional[str]]:
        """Tail log file."""
        if not os.path.exists(log_file):
            # Try common log locations
            common_logs = [
                "logs/app.log",
                "logs/error.log",
                "app.log",
                "server.log",
                "debug.log"
            ]
            for log in common_logs:
                if os.path.exists(log):
                    log_file = log
                    break
            else:
                return False, "", f"Log file not found: {log_file}"
        
        # Use platform-specific tail command
        if os.name == 'nt':  # Windows
            cmd = f'powershell -c "Get-Content \'{log_file}\' -Tail {lines}"'
        else:  # Unix-like
            cmd = f"tail -n {lines} {log_file}"
        
        result = self._run_command(cmd, timeout=10)
        
        if result["success"]:
            return True, result["stdout"], None
        else:
            return False, "", f"Failed to tail log: {result['stderr']}"
    
    def _run_shell(self, command: str, project_dir: str = None) -> tuple[bool, str, Optional[str]]:
        """Execute arbitrary shell command."""
        result = self._run_command(command, cwd=project_dir, timeout=60)
        
        output = result["stdout"] or result["stderr"]
        
        if result["success"]:
            return True, output, None
        else:
            return False, output, f"Command failed with exit code {result['returncode']}"
    
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
        project_dir = kwargs.get("project_dir", os.getcwd())
        package = kwargs.get("package", "")
        script = kwargs.get("script", "dev")
        log_file = kwargs.get("log_file", "")
        command = kwargs.get("command", "")
        lines = kwargs.get("lines", 50)
        
        try:
            if action == "open_vscode":
                success, output, error = self._open_vscode(project_dir)
                result = {"output": output, "project_dir": project_dir}
            
            elif action == "npm_install":
                success, output, error = self._npm_install(project_dir, package)
                result = {"output": output}
            
            elif action == "pip_install":
                success, output, error = self._pip_install(project_dir, package)
                result = {"output": output}
            
            elif action == "start_server":
                success, output, error = self._start_server(project_dir, script)
                result = {"output": output, "script": script}
            
            elif action == "tail_log":
                if not log_file:
                    return SkillResult(
                        success=False,
                        result=None,
                        error_message="log_file required for tail_log",
                        execution_time_ms=int((time.time() - start) * 1000)
                    )
                success, output, error = self._tail_log(log_file, lines)
                result = {"log_output": output, "lines": lines}
            
            elif action == "run_shell":
                if not command:
                    return SkillResult(
                        success=False,
                        result=None,
                        error_message="command required for run_shell",
                        execution_time_ms=int((time.time() - start) * 1000)
                    )
                success, output, error = self._run_shell(command, project_dir)
                result = {"output": output, "command": command}
            
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
            
        except Exception as e:
            logger.error(f"IDE controller failed: {e}")
            return SkillResult(
                success=False,
                result=None,
                error_message=str(e),
                execution_time_ms=int((time.time() - start) * 1000)
            )
