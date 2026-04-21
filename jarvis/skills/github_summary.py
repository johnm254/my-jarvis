"""GitHub Summary Skill for JARVIS using GitHub API.

Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6
"""

import os
import time
import logging
from typing import Any, Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
import requests

from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class GitHubSummarySkill(Skill):
    """
    GitHub summary skill that retrieves repository activity.
    
    Retrieves open pull requests, issues, and recent commits.
    Generates a Brain summary of repository activity.
    
    Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6
    """
    
    def __init__(self):
        """Initialize the GitHub summary skill."""
        super().__init__()
        self._name = "github_summary"
        self._description = "Summarize GitHub repository activity including open pull requests, issues, and recent commits. Generates a concise summary of repository status."
        self._parameters = {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository in format 'owner/repo' (e.g., 'facebook/react')"
                }
            },
            "required": ["repo"]
        }
        
        # GitHub token from environment
        self._github_token = os.getenv("GITHUB_TOKEN")
        self._timeout = 5  # 5 seconds timeout as per requirement 10.6
        self._base_url = "https://api.github.com"
    
    def _check_configuration(self) -> tuple[bool, Optional[str]]:
        """
        Check if GitHub token is configured.
        
        Returns:
            Tuple of (is_configured, error_message)
        """
        if not self._github_token:
            return False, "GitHub token not configured. Please set GITHUB_TOKEN in .env file."
        
        return True, None
    
    def _validate_repo_format(self, repo: str) -> tuple[bool, Optional[str]]:
        """
        Validate repository format.
        
        Args:
            repo: Repository string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if "/" not in repo:
            return False, f"Invalid repository format: '{repo}'. Expected format: 'owner/repo' (e.g., 'facebook/react')"
        
        parts = repo.split("/")
        if len(parts) != 2:
            return False, f"Invalid repository format: '{repo}'. Expected format: 'owner/repo'"
        
        owner, repo_name = parts
        if not owner or not repo_name:
            return False, f"Invalid repository format: '{repo}'. Owner and repo name cannot be empty"
        
        return True, None
    
    def _get_pull_requests(self, repo: str) -> tuple[bool, List[Dict], Optional[str]]:
        """
        Get open pull requests for a repository.
        
        Args:
            repo: Repository in format 'owner/repo'
            
        Returns:
            Tuple of (success, pull_requests, error_message)
        """
        try:
            headers = {
                "Authorization": f"token {self._github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            url = f"{self._base_url}/repos/{repo}/pulls"
            params = {
                "state": "open",
                "per_page": 100  # Get up to 100 PRs
            }
            
            # Use shorter timeout for individual requests since we're making parallel calls
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=min(self._timeout, 3)  # Max 3s per request
            )
            
            if response.status_code == 404:
                return False, [], f"Repository '{repo}' not found"
            
            if response.status_code != 200:
                return False, [], f"GitHub API returned status code {response.status_code}: {response.text}"
            
            prs = response.json()
            
            # Format PR data
            formatted_prs = []
            for pr in prs:
                formatted_prs.append({
                    "number": pr.get("number"),
                    "title": pr.get("title"),
                    "author": pr.get("user", {}).get("login"),
                    "created_at": pr.get("created_at"),
                    "updated_at": pr.get("updated_at"),
                    "url": pr.get("html_url")
                })
            
            return True, formatted_prs, None
            
        except requests.exceptions.Timeout:
            return False, [], f"Request to GitHub API timed out"
        except requests.exceptions.RequestException as e:
            return False, [], f"Network error communicating with GitHub API: {str(e)}"
        except Exception as e:
            return False, [], f"Error retrieving pull requests: {str(e)}"
    
    def _get_issues(self, repo: str) -> tuple[bool, List[Dict], Optional[str]]:
        """
        Get open issues for a repository.
        
        Args:
            repo: Repository in format 'owner/repo'
            
        Returns:
            Tuple of (success, issues, error_message)
        """
        try:
            headers = {
                "Authorization": f"token {self._github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            url = f"{self._base_url}/repos/{repo}/issues"
            params = {
                "state": "open",
                "per_page": 100  # Get up to 100 issues
            }
            
            # Use shorter timeout for individual requests since we're making parallel calls
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=min(self._timeout, 3)  # Max 3s per request
            )
            
            if response.status_code == 404:
                return False, [], f"Repository '{repo}' not found"
            
            if response.status_code != 200:
                return False, [], f"GitHub API returned status code {response.status_code}: {response.text}"
            
            issues = response.json()
            
            # Filter out pull requests (GitHub API returns PRs as issues)
            # Format issue data
            formatted_issues = []
            for issue in issues:
                # Skip if it's a pull request
                if "pull_request" in issue:
                    continue
                
                formatted_issues.append({
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "author": issue.get("user", {}).get("login"),
                    "created_at": issue.get("created_at"),
                    "updated_at": issue.get("updated_at"),
                    "labels": [label.get("name") for label in issue.get("labels", [])],
                    "url": issue.get("html_url")
                })
            
            return True, formatted_issues, None
            
        except requests.exceptions.Timeout:
            return False, [], f"Request to GitHub API timed out"
        except requests.exceptions.RequestException as e:
            return False, [], f"Network error communicating with GitHub API: {str(e)}"
        except Exception as e:
            return False, [], f"Error retrieving issues: {str(e)}"
    
    def _get_commits(self, repo: str) -> tuple[bool, List[Dict], Optional[str]]:
        """
        Get last 10 commits for a repository.
        
        Args:
            repo: Repository in format 'owner/repo'
            
        Returns:
            Tuple of (success, commits, error_message)
        """
        try:
            headers = {
                "Authorization": f"token {self._github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            url = f"{self._base_url}/repos/{repo}/commits"
            params = {
                "per_page": 10  # Get last 10 commits as per requirement 10.4
            }
            
            # Use shorter timeout for individual requests since we're making parallel calls
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=min(self._timeout, 3)  # Max 3s per request
            )
            
            if response.status_code == 404:
                return False, [], f"Repository '{repo}' not found"
            
            if response.status_code != 200:
                return False, [], f"GitHub API returned status code {response.status_code}: {response.text}"
            
            commits = response.json()
            
            # Format commit data
            formatted_commits = []
            for commit in commits:
                formatted_commits.append({
                    "sha": commit.get("sha", "")[:7],  # Short SHA
                    "message": commit.get("commit", {}).get("message", "").split("\n")[0],  # First line only
                    "author": commit.get("commit", {}).get("author", {}).get("name"),
                    "date": commit.get("commit", {}).get("author", {}).get("date"),
                    "url": commit.get("html_url")
                })
            
            return True, formatted_commits, None
            
        except requests.exceptions.Timeout:
            return False, [], f"Request to GitHub API timed out"
        except requests.exceptions.RequestException as e:
            return False, [], f"Network error communicating with GitHub API: {str(e)}"
        except Exception as e:
            return False, [], f"Error retrieving commits: {str(e)}"
    
    def _generate_summary(
        self,
        repo: str,
        prs: List[Dict],
        issues: List[Dict],
        commits: List[Dict]
    ) -> str:
        """
        Generate a Brain-style summary of repository activity.
        
        Args:
            repo: Repository name
            prs: List of pull requests
            issues: List of issues
            commits: List of commits
            
        Returns:
            Human-readable summary
        """
        summary_parts = []
        
        # Repository header
        summary_parts.append(f"GitHub Repository Summary for {repo}:")
        summary_parts.append("")
        
        # Pull requests summary
        if prs:
            summary_parts.append(f"Open Pull Requests ({len(prs)}):")
            for pr in prs[:5]:  # Show top 5
                summary_parts.append(f"  - #{pr['number']}: {pr['title']} by {pr['author']}")
            if len(prs) > 5:
                summary_parts.append(f"  ... and {len(prs) - 5} more")
        else:
            summary_parts.append("No open pull requests")
        
        summary_parts.append("")
        
        # Issues summary
        if issues:
            summary_parts.append(f"Open Issues ({len(issues)}):")
            for issue in issues[:5]:  # Show top 5
                labels_str = f" [{', '.join(issue['labels'])}]" if issue['labels'] else ""
                summary_parts.append(f"  - #{issue['number']}: {issue['title']}{labels_str}")
            if len(issues) > 5:
                summary_parts.append(f"  ... and {len(issues) - 5} more")
        else:
            summary_parts.append("No open issues")
        
        summary_parts.append("")
        
        # Recent commits summary
        if commits:
            summary_parts.append(f"Recent Commits (last {len(commits)}):")
            for commit in commits:
                summary_parts.append(f"  - {commit['sha']}: {commit['message']} by {commit['author']}")
        else:
            summary_parts.append("No recent commits")
        
        return "\n".join(summary_parts)
    
    def execute(self, **kwargs) -> SkillResult:
        """
        Execute GitHub repository summary.
        
        Args:
            **kwargs: Must contain 'repo' parameter
            
        Returns:
            SkillResult with repository activity summary
            
        Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6
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
        
        repo = kwargs.get("repo")
        
        # Validate repository format
        format_valid, format_error = self._validate_repo_format(repo)
        if not format_valid:
            return SkillResult(
                success=False,
                result=None,
                error_message=format_error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Check configuration
        config_ok, config_error = self._check_configuration()
        if not config_ok:
            return SkillResult(
                success=False,
                result=None,
                error_message=config_error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Optimize by making parallel API calls instead of sequential
        # This significantly improves performance for requirement 10.6 (< 5s)
        prs = []
        issues = []
        commits = []
        errors = []
        
        try:
            # Use ThreadPoolExecutor to make parallel API calls
            with ThreadPoolExecutor(max_workers=3) as executor:
                # Submit all three API calls concurrently
                future_prs = executor.submit(self._get_pull_requests, repo)
                future_issues = executor.submit(self._get_issues, repo)
                future_commits = executor.submit(self._get_commits, repo)
                
                # Calculate remaining time for timeout
                elapsed = time.time() - start_time
                remaining_timeout = max(0.5, self._timeout - elapsed)
                
                # Collect results with timeout
                futures = {
                    'prs': future_prs,
                    'issues': future_issues,
                    'commits': future_commits
                }
                
                for name, future in futures.items():
                    try:
                        success, data, error = future.result(timeout=remaining_timeout)
                        if not success:
                            errors.append(f"{name}: {error}")
                        else:
                            if name == 'prs':
                                prs = data
                            elif name == 'issues':
                                issues = data
                            elif name == 'commits':
                                commits = data
                    except FuturesTimeoutError:
                        errors.append(f"{name}: Request timed out")
                        logger.error(f"Timeout fetching {name} for repo '{repo}'")
                    except Exception as e:
                        errors.append(f"{name}: {str(e)}")
                        logger.error(f"Error fetching {name} for repo '{repo}': {str(e)}")
            
            # If all requests failed, return error
            if len(errors) == 3:
                return SkillResult(
                    success=False,
                    result=None,
                    error_message=f"All GitHub API requests failed: {'; '.join(errors)}",
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )
            
            # Generate summary even with partial data (requirement 10.5)
            summary = self._generate_summary(repo, prs, issues, commits)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log performance metrics
            logger.info(f"GitHub summary completed for '{repo}' in {execution_time}ms")
            
            # Warn if approaching timeout threshold (requirement 10.6: < 5s)
            if execution_time > 4500:
                logger.warning(f"GitHub summary for '{repo}' took {execution_time}ms (approaching 5s limit)")
            
            # Log any partial failures
            if errors:
                logger.warning(f"GitHub summary for '{repo}' completed with partial failures: {'; '.join(errors)}")
            
            result = {
                "repo": repo,
                "pull_requests": prs,
                "pull_requests_count": len(prs),
                "issues": issues,
                "issues_count": len(issues),
                "commits": commits,
                "commits_count": len(commits),
                "summary": summary,
                "partial_failures": errors if errors else None
            }
            
            return SkillResult(
                success=True,
                result=result,
                error_message=None,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Unexpected error during GitHub summary: {str(e)}"
            logger.error(f"Unexpected error for repo '{repo}': {error_msg}")
            return SkillResult(
                success=False,
                result=None,
                error_message=error_msg,
                execution_time_ms=execution_time
            )
