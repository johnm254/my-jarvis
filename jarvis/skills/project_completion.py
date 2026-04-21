"""Skill 6 — Completion & Notification

Sends completion notification when project is done:
- Email summary via Gmail API
- Include repo link, PR link
- Summary of what was built
- Any warnings or issues
"""

import os
import time
import logging
from typing import Any, Dict, Optional, List
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class ProjectCompletionSkill(Skill):
    """
    Project completion & notification skill.
    
    Sends email notification when project delivery is complete:
    - Repo link
    - PR link
    - Summary of features built
    - Warnings/issues
    - Test results
    """
    
    def __init__(self):
        super().__init__()
        self._name = "project_completion"
        self._description = (
            "Send completion notification email with repo link, PR link, "
            "summary of what was built, and any warnings."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "recipient": {
                    "type": "string",
                    "description": "Email recipient address"
                },
                "project_name": {
                    "type": "string",
                    "description": "Project name"
                },
                "repo_url": {
                    "type": "string",
                    "description": "GitHub repository URL"
                },
                "pr_url": {
                    "type": "string",
                    "description": "Pull request URL"
                },
                "features": {
                    "type": "array",
                    "description": "List of features implemented",
                    "items": {"type": "string"}
                },
                "warnings": {
                    "type": "array",
                    "description": "List of warnings or issues",
                    "items": {"type": "string"}
                },
                "test_results": {
                    "type": "object",
                    "description": "Test results summary"
                }
            },
            "required": ["recipient", "project_name"]
        }
        
        self._gmail_credentials = os.getenv("GMAIL_CREDENTIALS")
    
    def _generate_email_body(
        self,
        project_name: str,
        repo_url: Optional[str],
        pr_url: Optional[str],
        features: List[str],
        warnings: List[str],
        test_results: Optional[Dict[str, Any]]
    ) -> str:
        """Generate HTML email body."""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #4CAF50; }}
        .warning {{ border-left-color: #ff9800; }}
        .link {{ color: #2196F3; text-decoration: none; }}
        .feature-list {{ list-style: none; padding: 0; }}
        .feature-list li {{ padding: 5px 0; }}
        .feature-list li:before {{ content: "✓ "; color: #4CAF50; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Project Complete: {project_name}</h1>
        </div>
        
        <div class="section">
            <h2>Project Links</h2>
            <p><strong>Repository:</strong> <a href="{repo_url or '#'}" class="link">{repo_url or 'N/A'}</a></p>
            <p><strong>Pull Request:</strong> <a href="{pr_url or '#'}" class="link">{pr_url or 'N/A'}</a></p>
        </div>
        
        <div class="section">
            <h2>Features Implemented</h2>
            <ul class="feature-list">
"""
        
        for feature in features:
            html += f"                <li>{feature}</li>\n"
        
        html += """            </ul>
        </div>
"""
        
        if test_results:
            html += f"""
        <div class="section">
            <h2>Test Results</h2>
            <p><strong>Tests Passed:</strong> {test_results.get('passed', 'N/A')}</p>
            <p><strong>Tests Failed:</strong> {test_results.get('failed', 0)}</p>
            <p><strong>Coverage:</strong> {test_results.get('coverage', 'N/A')}</p>
        </div>
"""
        
        if warnings:
            html += """
        <div class="section warning">
            <h2>⚠️ Warnings & Issues</h2>
            <ul>
"""
            for warning in warnings:
                html += f"                <li>{warning}</li>\n"
            
            html += """            </ul>
        </div>
"""
        
        html += """
        <div class="section">
            <p><em>This project was automatically generated and deployed by JARVIS.</em></p>
            <p>Review the code, run tests locally, and merge the PR when ready.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def _send_email(
        self,
        recipient: str,
        subject: str,
        body_html: str
    ) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Send email via Gmail API."""
        if not self._gmail_credentials:
            return False, {}, "Gmail credentials not configured"
        
        # TODO: Integrate with Gmail MCP tool to send email
        # For now, return mock success
        
        logger.info(f"Would send email to {recipient}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body length: {len(body_html)} chars")
        
        return True, {
            "recipient": recipient,
            "subject": subject,
            "status": "sent (mock)",
            "message": "Gmail MCP integration pending. Email content generated successfully."
        }, None
    
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
        
        recipient = kwargs.get("recipient")
        project_name = kwargs.get("project_name")
        repo_url = kwargs.get("repo_url")
        pr_url = kwargs.get("pr_url")
        features = kwargs.get("features", [])
        warnings = kwargs.get("warnings", [])
        test_results = kwargs.get("test_results")
        
        # Generate email
        subject = f"✅ Project Complete: {project_name}"
        body_html = self._generate_email_body(
            project_name,
            repo_url,
            pr_url,
            features,
            warnings,
            test_results
        )
        
        # Send email
        success, result, error = self._send_email(recipient, subject, body_html)
        
        if success:
            result["email_preview"] = body_html[:500] + "..."
        
        return SkillResult(
            success=success,
            result=result,
            error_message=error,
            execution_time_ms=int((time.time() - start) * 1000)
        )
