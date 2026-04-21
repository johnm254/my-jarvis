"""Skill 5 — IDE & Local Environment Control

Controls local development environment:
- Open projects in VS Code
- Run package managers (npm install, pip install)
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


class IDEControlSkill(Skill):
    """
    IDE & local environment control skill.
    
    Features:
    - Open VS Code
    - Run npm install / pip install
    - Start dev servers
    - Tail logs
    - Execute shell commands
    - System automation (AppleScript/xdg-open)
    """
    
    def __init__(self):
        super().__init__()
        self._name = "ide_control"
        self._description = (
            "Control local development environment: open VS Code, "
            "install packages, start dev servers, tail logs, run commands."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action: 'open_vscode', 'install_deps', 'start_server', 'tail_log', 'run_command'",
                    "enum": ["open_vscode", "install_deps", "start_server", "tail_log", "run_command"]
                },
                "project_path": {
                    "type": "string",
                    "description": "Path to project directory"
                },
                "package_manager": {
                    "type": "string",
                    "description": "Package manager: 'npm', 'pip', 'yarn', 'pnpm'",
                    "enum": ["npm", "pip", "yarn", "pnpm"]
                },
                "server_command": {
                    "type": "string",
                    "description": "Command to start dev server (e.g., 'npm run dev', 'uvicorn main:app --reload')"
                },
                "log_file": {
                    "type": "string",
                    "description": "Path to log file to tail"
                },
                "command": {
                    "type": "string",
                    "description": "Shell command to execute"
                }
            },
            "required": ["action"]
        }
    
    def _run_command(self, cmd: str, cwd: str = None, timeout: int = 60, background: bool = False) -> Dict[str, Any]:
        """Run shell command."""
        try:
            if background:
                # Start in background
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
            return {"stdout": "", "stderr": "Timeout", "returncode": -1, "success": False}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": -1, "success": False}
    
    def _open_vscode(self, project_path: str) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Open project in VS Code."""
        if not os.path.exists(project_path):
            return False, {}, f"Project path not found: {project_path}"
        
        cmd = f'code "{project_path}"'
        result = self._run_command(cmd, background=True)
        
        return True, {
            "project_path": os.path.abspath(project_path),
            "message": "Opened in VS Code"
        }, None
    
    def _install_deps(self, project_path: str, package_manager: str) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Install project dependencies."""
        if not os.path.exists(project_path):
            return False, {}, f"Project path not found: {project_path}"
        
        # Determine install command
        install_commands = {
            "npm": "npm install",
            "yarn": "yarn install",
            "pnpm": "pnpm install",
            "pip": "pip install -r requirements.txt"
        }
        
        cmd = install_commands.get(package_manager)
        if not cmd:
            return False, {}, f"Unknown package manager: {package_manager}"
        
        # Check if package file exists
        package_files = {
            "npm": "package.json",
            "yarn": "package.json",
            "pnpm": "package.json",
            "pip": "requirements.txt"
        }
        
        package_file = os.path.join(project_path, package_files[package_manager])
        if not os.path.exists(package_file):
            return False, {}, f"Package file not found: {package_files[package_manager]}"
        
        result = self._run_command(cmd, cwd=project_path, timeout=300)
        
        if result["success"]:
            return True, {
                "package_manager": package_manager,
                "message": "Dependencies installed successfully"
            }, None
        else:
            return False, {}, f"Installation failed: {result['stderr']}"
    
    def _start_server(self, project_path: str, server_command: str) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Start development server in background."""
        if not os.path.exists(project_path):
            return False, {}, f"Project path not found: {project_path}"
        
        if not server_command:
            # Try to detect server command
            if os.path.exists(os.path.join(project_path, "package.json")):
                server_command = "npm run dev"
            elif os.path.exists(os.path.join(project_path, "main.py")):
                server_command = "uvicorn main:app --reload"
            else:
                return False, {}, "Could not detect server command. Please specify server_command parameter."
        
        result = self._run_command(server_command, cwd=project_path, background=True)
        
        return True, {
            "server_command": server_command,
            "project_path": os.path.abspath(project_path),
            "message": "Dev server started in background"
        }, None
    
    def _tail_log(self, log_file: str, lines: int = 50) -> tuple[bool, Dict[str, Any], Optional[str]]:
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
                return False, {}, f"Log file not found: {log_file}"
        
        # Use PowerShell Get-Content on Windows
        cmd = f'powershell -c "Get-Content \'{log_file}\' -Tail {lines}"'
        result = self._run_command(cmd)
        
        if result["success"]:
            return True, {
                "log_file": os.path.abspath(log_file),
                "content": result["stdout"]
            }, None
        else:
            return False, {}, f"Failed to read log: {result['stderr']}"
    
    def _run_custom_command(self, command: str, project_path: str = None) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Execute custom shell command."""
        result = self._run_command(command, cwd=project_path, timeout=120)
        
        return result["success"], {
            "command": command,
            "stdout": result["stdout"],
            "stderr": result["stderr"]
        }, None if result["success"] else result["stderr"]
    
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
        project_path = kwargs.get("project_path", os.getcwd())
        
        if action == "open_vscode":
            success, result, error = self._open_vscode(project_path)
        
        elif action == "install_deps":
            package_manager = kwargs.get("package_manager", "npm")
            success, result, error = self._install_deps(project_path, package_manager)
        
        elif action == "start_server":
            server_command = kwargs.get("server_command")
            success, result, error = self._start_server(project_path, server_command)
        
        elif action == "tail_log":
            log_file = kwargs.get("log_file", "app.log")
            success, result, error = self._tail_log(log_file)
        
        elif action == "run_command":
            command = kwargs.get("command")
            if not command:
                return SkillResult(
                    success=False,
                    result=None,
                    error_message="command required for run_command action",
                    execution_time_ms=int((time.time() - start) * 1000)
                )
            success, result, error = self._run_custom_command(command, project_path)
        
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
