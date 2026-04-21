"""Skill 4 — GitHub & Version Control

Manages GitHub operations:
- Create repositories
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


class GitHubManagerSkill(Skill):
    """
    GitHub & version control management skill.
    
    Features:
    - Create GitHub repositories
    - Push code with meaningful commits
    - Create dev branches
    - Open pull requests
    - Clone/fetch existing repositories
    """
    
    def __init__(self):
        super().__init__()
        self._name = "github_manager"
        self._description = (
            "Manage GitHub operations: create repos, push code, "
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
                "project_dir": {
                    "type": "string",
                    "description": "Local project directory"
                },
                "branch_name": {
                    "type": "string",
                    "description": "Branch name (for create_branch, open_pr)"
                },
                "commit_message": {
                    "type": "string",
                    "description": "Commit message (for push)"
                },
                "pr_title": {
                    "type": "string",
                    "description": "Pull request title (for open_pr)"
                },
                "pr_body": {
                    "type": "string",
                    "description": "Pull request description (for open_pr)"
                },
                "private": {
                    "type": "boolean",
                    "description": "Create private repository (default: false)"
                }
            },
            "required": ["action"]
        }
        
        self._github_token = os.getenv("GITHUB_TOKEN")
    
    def _run_command(self, cmd: str, cwd: str = None, timeout: int = 60) -> Dict[str, Any]:
        """Run shell command and return result."""
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
            return {"stdout": "", "stderr": "Command timed out", "returncode": -1, "success": False}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": -1, "success": False}
    
    def _create_repo(self, repo_name: str, private: bool = False) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Create a new GitHub repository using GitHub CLI or API."""
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
            # TODO: Implement GitHub REST API call
            return False, {}, f"Failed to create repo: {result['stderr']}"
    
    def _push_code(self, project_dir: str, commit_message: str = None) -> tuple[bool, str, Optional[str]]:
        """Push code to GitHub with meaningful commit message."""
        if not commit_message:
            commit_message = "Auto-commit by JARVIS"
        
        # Git add all
        result = self._run_command("git add -A", cwd=project_dir)
        if not result["success"]:
            return False, "", f"git add failed: {result['stderr']}"
        
        # Git commit
        result = self._run_command(f'git commit -m "{commit_message}"', cwd=project_dir)
        if not result["success"] and "nothing to commit" not in result["stdout"]:
            return False, "", f"git commit failed: {result['stderr']}"
        
        # Git push
        result = self._run_command("git push origin HEAD", cwd=project_dir, timeout=120)
        if not result["success"]:
            return False, "", f"git push failed: {result['stderr']}"
        
        return True, result["stdout"], None
    
    def _create_branch(self, project_dir: str, branch_name: str) -> tuple[bool, str, Optional[str]]:
        """Create a new branch."""
        result = self._run_command(f"git checkout -b {branch_name}", cwd=project_dir)
        
        if result["success"]:
            return True, f"Created and switched to branch: {branch_name}", None
        else:
            return False, "", f"Failed to create branch: {result['stderr']}"
    
    def _open_pr(self, project_dir: str, branch_name: str, pr_title: str, pr_body: str = "") -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Open a pull request using GitHub CLI."""
        if not self._github_token:
            return False, {}, "GITHUB_TOKEN not configured"
        
        if not pr_title:
            pr_title = f"Feature: {branch_name}"
        
        if not pr_body:
            pr_body = "Auto-generated PR by JARVIS"
        
        # Use GitHub CLI to create PR
        cmd = f'gh pr create --title "{pr_title}" --body "{pr_body}" --base main --head {branch_name}'
        result = self._run_command(cmd, cwd=project_dir)
        
        if result["success"]:
            pr_url = result["stdout"]
            return True, {
                "pr_url": pr_url,
                "title": pr_title,
                "branch": branch_name
            }, None
        else:
            return False, {}, f"Failed to create PR: {result['stderr']}"
    
    def _clone_repo(self, repo_name: str, target_dir: str = None) -> tuple[bool, str, Optional[str]]:
        """Clone a GitHub repository."""
        if not target_dir:
            target_dir = os.path.join("jarvis_output", "cloned_repos", repo_name.split('/')[-1])
        
        os.makedirs(os.path.dirname(target_dir), exist_ok=True)
        
        cmd = f"git clone https://github.com/{repo_name}.git {target_dir}"
        result = self._run_command(cmd, timeout=180)
        
        if result["success"]:
            return True, os.path.abspath(target_dir), None
        else:
            return False, "", f"Failed to clone repo: {result['stderr']}"
    
    def _fetch_repo(self, project_dir: str) -> tuple[bool, str, Optional[str]]:
        """Fetch latest changes from remote."""
        result = self._run_command("git fetch origin", cwd=project_dir, timeout=120)
        
        if result["success"]:
            return True, "Fetched latest changes", None
        else:
            return False, "", f"Failed to fetch: {result['stderr']}"
    
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
        repo_name = kwargs.get("repo_name", "")
        project_dir = kwargs.get("project_dir", os.getcwd())
        branch_name = kwargs.get("branch_name", "dev")
        commit_message = kwargs.get("commit_message", "")
        pr_title = kwargs.get("pr_title", "")
        pr_body = kwargs.get("pr_body", "")
        private = kwargs.get("private", False)
        
        try:
            if action == "create_repo":
                if not repo_name:
                    return SkillResult(
                        success=False,
                        result=None,
                        error_message="repo_name required for create_repo",
                        execution_time_ms=int((time.time() - start) * 1000)
                    )
                success, result, error = self._create_repo(repo_name, private)
            
            elif action == "push":
                success, output, error = self._push_code(project_dir, commit_message)
                result = {"output": output, "project_dir": project_dir}
            
            elif action == "create_branch":
                success, output, error = self._create_branch(project_dir, branch_name)
                result = {"output": output, "branch": branch_name}
            
            elif action == "open_pr":
                success, result, error = self._open_pr(project_dir, branch_name, pr_title, pr_body)
            
            elif action == "clone":
                if not repo_name:
                    return SkillResult(
                        success=False,
                        result=None,
                        error_message="repo_name required for clone",
                        execution_time_ms=int((time.time() - start) * 1000)
                    )
                success, cloned_dir, error = self._clone_repo(repo_name, project_dir)
                result = {"cloned_to": cloned_dir}
            
            elif action == "fetch":
                success, output, error = self._fetch_repo(project_dir)
                result = {"output": output}
            
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
            logger.error(f"GitHub manager failed: {e}")
            return SkillResult(
                success=False,
                result=None,
                error_message=str(e),
                execution_time_ms=int((time.time() - start) * 1000)
            )
