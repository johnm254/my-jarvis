"""Skill 4 — GitHub & Version Control

Automates GitHub operations:
- Create repository
- Push code with meaningful commits
- Create branches
- Open pull requests
- Clone/fetch existing repos
"""

import os
import json
import time
import subprocess
import logging
from typing import Any, Dict, Optional
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class GitHubAutomationSkill(Skill):
    """
    GitHub & version control automation skill.
    
    Features:
    - Create GitHub repository
    - Push generated code
    - Create dev branch
    - Open pull request
    - Clone/fetch repos
    - Meaningful commit messages
    """
    
    def __init__(self):
        super().__init__()
        self._name = "github_automation"
        self._description = (
            "Automate GitHub operations: create repo, push code, "
            "create branches, open PRs, clone/fetch repos."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action: 'create_repo', 'push', 'create_branch', 'open_pr', 'clone', 'fetch'",
                    "enum": ["create_repo", "push", "create_branch", "open_pr", "clone", "fetch"]
                },
                "repo_name": {
                    "type": "string",
                    "description": "Repository name"
                },
                "repo_url": {
                    "type": "string",
                    "description": "Repository URL (for clone/fetch)"
                },
                "local_path": {
                    "type": "string",
                    "description": "Local path to code"
                },
                "branch_name": {
                    "type": "string",
                    "description": "Branch name (for create_branch)"
                },
                "commit_message": {
                    "type": "string",
                    "description": "Commit message"
                },
                "pr_title": {
                    "type": "string",
                    "description": "Pull request title"
                },
                "pr_body": {
                    "type": "string",
                    "description": "Pull request description"
                },
                "private": {
                    "type": "boolean",
                    "description": "Make repo private (default: false)"
                }
            },
            "required": ["action"]
        }
        
        self._github_token = os.getenv("GITHUB_TOKEN")
    
    def _run_command(self, cmd: str, cwd: str = None, timeout: int = 60) -> Dict[str, Any]:
        """Run shell command."""
        try:
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
    
    def _create_repo(self, repo_name: str, private: bool = False) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Create GitHub repository using GitHub CLI or API."""
        if not self._github_token:
            return False, {}, "GITHUB_TOKEN not configured"
        
        # Try using GitHub CLI (gh)
        visibility = "private" if private else "public"
        cmd = f'gh repo create {repo_name} --{visibility} --source=. --remote=origin'
        
        result = self._run_command(cmd)
        
        if result["success"]:
            return True, {
                "repo_name": repo_name,
                "visibility": visibility,
                "url": f"https://github.com/{repo_name}"
            }, None
        else:
            # Fallback: use GitHub API
            # TODO: Implement GitHub API call
            return False, {}, f"Failed to create repo: {result['stderr']}"
    
    def _push_code(self, local_path: str, commit_message: str = None) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Push code to GitHub with meaningful commit."""
        if not commit_message:
            # Generate meaningful commit message
            commit_message = "feat: initial project setup with generated code"
        
        # Git operations
        commands = [
            "git add -A",
            f'git commit -m "{commit_message}"',
            "git push -u origin main"
        ]
        
        for cmd in commands:
            result = self._run_command(cmd, cwd=local_path)
            if not result["success"] and "nothing to commit" not in result["stdout"]:
                return False, {}, f"Git command failed: {cmd}\n{result['stderr']}"
        
        return True, {
            "commit_message": commit_message,
            "branch": "main"
        }, None
    
    def _create_branch(self, local_path: str, branch_name: str) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Create and checkout a new branch."""
        cmd = f"git checkout -b {branch_name}"
        result = self._run_command(cmd, cwd=local_path)
        
        if result["success"]:
            # Push branch to remote
            push_result = self._run_command(f"git push -u origin {branch_name}", cwd=local_path)
            return True, {"branch": branch_name}, None
        else:
            return False, {}, f"Failed to create branch: {result['stderr']}"
    
    def _open_pr(self, local_path: str, pr_title: str, pr_body: str = None) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Open a pull request using GitHub CLI."""
        if not self._github_token:
            return False, {}, "GITHUB_TOKEN not configured"
        
        if not pr_body:
            pr_body = "Automated PR created by JARVIS"
        
        cmd = f'gh pr create --title "{pr_title}" --body "{pr_body}"'
        result = self._run_command(cmd, cwd=local_path)
        
        if result["success"]:
            pr_url = result["stdout"]
            return True, {
                "pr_title": pr_title,
                "pr_url": pr_url
            }, None
        else:
            return False, {}, f"Failed to create PR: {result['stderr']}"
    
    def _clone_repo(self, repo_url: str, local_path: str = None) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Clone a GitHub repository."""
        if not local_path:
            # Extract repo name from URL
            repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
            local_path = os.path.join(os.getcwd(), repo_name)
        
        cmd = f'git clone {repo_url} "{local_path}"'
        result = self._run_command(cmd, timeout=120)
        
        if result["success"]:
            return True, {
                "repo_url": repo_url,
                "local_path": os.path.abspath(local_path)
            }, None
        else:
            return False, {}, f"Failed to clone: {result['stderr']}"
    
    def _fetch_repo(self, local_path: str) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Fetch latest changes from remote."""
        commands = [
            "git fetch origin",
            "git pull origin main"
        ]
        
        for cmd in commands:
            result = self._run_command(cmd, cwd=local_path)
            if not result["success"]:
                return False, {}, f"Failed to fetch: {result['stderr']}"
        
        return True, {"local_path": local_path}, None
    
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
        
        if action == "create_repo":
            repo_name = kwargs.get("repo_name")
            private = kwargs.get("private", False)
            if not repo_name:
                return SkillResult(
                    success=False,
                    result=None,
                    error_message="repo_name required for create_repo",
                    execution_time_ms=int((time.time() - start) * 1000)
                )
            success, result, error = self._create_repo(repo_name, private)
        
        elif action == "push":
            local_path = kwargs.get("local_path", os.getcwd())
            commit_message = kwargs.get("commit_message")
            success, result, error = self._push_code(local_path, commit_message)
        
        elif action == "create_branch":
            local_path = kwargs.get("local_path", os.getcwd())
            branch_name = kwargs.get("branch_name", "dev")
            success, result, error = self._create_branch(local_path, branch_name)
        
        elif action == "open_pr":
            local_path = kwargs.get("local_path", os.getcwd())
            pr_title = kwargs.get("pr_title", "Automated PR")
            pr_body = kwargs.get("pr_body")
            success, result, error = self._open_pr(local_path, pr_title, pr_body)
        
        elif action == "clone":
            repo_url = kwargs.get("repo_url")
            local_path = kwargs.get("local_path")
            if not repo_url:
                return SkillResult(
                    success=False,
                    result=None,
                    error_message="repo_url required for clone",
                    execution_time_ms=int((time.time() - start) * 1000)
                )
            success, result, error = self._clone_repo(repo_url, local_path)
        
        elif action == "fetch":
            local_path = kwargs.get("local_path", os.getcwd())
            success, result, error = self._fetch_repo(local_path)
        
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
