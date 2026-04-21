"""
Email Monitor Daemon

Monitors Gmail inbox for project requirement emails and automatically
triggers the full-stack automation workflow.
"""

import os
import time
import logging
import argparse
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment
load_dotenv()

from jarvis.skills.email_intake import EmailIntakeSkill
from jarvis.skills.project_architect import ProjectArchitectSkill
from jarvis.skills.code_generator import CodeGeneratorSkill
from jarvis.skills.github_automation import GitHubAutomationSkill
from jarvis.skills.ide_control import IDEControlSkill
from jarvis.skills.project_completion import ProjectCompletionSkill

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailMonitor:
    """Monitor Gmail inbox for project requirement emails."""
    
    def __init__(self, check_interval: int = 300):
        """
        Initialize email monitor.
        
        Args:
            check_interval: Seconds between inbox checks (default: 5 minutes)
        """
        self.check_interval = check_interval
        self.email_skill = EmailIntakeSkill()
        self.processed_emails = set()  # Track processed email IDs
        
        # Get configuration
        self.inbox_email = os.getenv("JARVIS_INBOX_EMAIL", os.getenv("NOTIFICATION_EMAIL"))
        self.inbox_label = os.getenv("JARVIS_INBOX_LABEL", "JARVIS Projects")
        
        logger.info(f"Email Monitor initialized")
        logger.info(f"Monitoring: {self.inbox_email}")
        logger.info(f"Check interval: {check_interval}s")
    
    def check_inbox(self) -> List[Dict[str, Any]]:
        """
        Check inbox for new project emails.
        
        Returns:
            List of new project emails
        """
        logger.info("Checking inbox for new project emails...")
        
        # TODO: Implement actual Gmail API integration
        # For now, return empty list
        
        # This would use Gmail API to:
        # 1. Search for emails with label or subject containing [JARVIS]
        # 2. Filter out already processed emails
        # 3. Return list of new emails
        
        return []
    
    def is_project_email(self, email: Dict[str, Any]) -> bool:
        """
        Check if email is a project requirement email.
        
        Args:
            email: Email data
            
        Returns:
            True if email contains project requirements
        """
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()
        
        # Keywords that indicate project email
        keywords = [
            "[jarvis]",
            "project name:",
            "stack:",
            "features:",
            "requirements:",
            "build a",
            "create a",
            "need a project"
        ]
        
        return any(kw in subject or kw in body for kw in keywords)
    
    def process_email(self, email: Dict[str, Any]) -> bool:
        """
        Process a project requirement email.
        
        Args:
            email: Email data
            
        Returns:
            True if processing succeeded
        """
        email_id = email.get("id")
        subject = email.get("subject")
        body = email.get("body")
        sender = email.get("from")
        
        logger.info(f"Processing email: {subject}")
        logger.info(f"From: {sender}")
        
        try:
            # Step 1: Extract requirements
            logger.info("Step 1: Extracting requirements...")
            result = self.email_skill.execute(
                action="parse",
                email_body=body,
                output_path=f"jarvis_output/specs/email_{email_id}.json"
            )
            
            if not result.success:
                logger.error(f"Failed to extract requirements: {result.error_message}")
                return False
            
            spec_path = result.result["saved_to"]
            project_name = result.result["spec"]["project_name"]
            
            logger.info(f"✅ Requirements extracted: {project_name}")
            
            # Send confirmation email
            self._send_confirmation(sender, project_name, spec_path)
            
            # Step 2: Generate architecture
            logger.info("Step 2: Generating architecture...")
            architect_skill = ProjectArchitectSkill()
            result = architect_skill.execute(
                spec_path=spec_path,
                output_dir=f"jarvis_output/architecture/{project_name}"
            )
            
            if not result.success:
                logger.error(f"Failed to generate architecture: {result.error_message}")
                return False
            
            logger.info(f"✅ Architecture generated")
            
            # Send architecture for review
            self._send_architecture_review(sender, project_name, result.result)
            
            # Mark as processed
            self.processed_emails.add(email_id)
            
            logger.info(f"✅ Email processed successfully: {email_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing email: {e}")
            return False
    
    def _send_confirmation(self, to: str, project_name: str, spec_path: str):
        """Send confirmation email that requirements were received."""
        logger.info(f"Sending confirmation to {to}")
        
        # TODO: Implement email sending
        # For now, just log
        logger.info(f"Confirmation: Requirements received for {project_name}")
    
    def _send_architecture_review(self, to: str, project_name: str, architecture: Dict[str, Any]):
        """Send architecture for review and approval."""
        logger.info(f"Sending architecture review to {to}")
        
        # TODO: Implement email sending with architecture files
        logger.info(f"Architecture ready for review: {project_name}")
        logger.info("Reply 'Approved' to start code generation")
    
    def run_once(self):
        """Run one check cycle."""
        try:
            emails = self.check_inbox()
            
            if not emails:
                logger.info("No new project emails found")
                return
            
            logger.info(f"Found {len(emails)} new email(s)")
            
            for email in emails:
                email_id = email.get("id")
                
                # Skip if already processed
                if email_id in self.processed_emails:
                    continue
                
                # Check if it's a project email
                if not self.is_project_email(email):
                    logger.info(f"Skipping non-project email: {email.get('subject')}")
                    continue
                
                # Process the email
                self.process_email(email)
                
        except Exception as e:
            logger.error(f"Error in check cycle: {e}")
    
    def run_daemon(self):
        """Run as daemon, checking inbox periodically."""
        logger.info("Starting email monitor daemon...")
        logger.info(f"Press Ctrl+C to stop")
        
        try:
            while True:
                self.run_once()
                
                logger.info(f"Sleeping for {self.check_interval}s...")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Email monitor stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in daemon: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="JARVIS Email Monitor")
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon (continuous monitoring)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Check interval in seconds (default: 300 = 5 minutes)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit"
    )
    
    args = parser.parse_args()
    
    monitor = EmailMonitor(check_interval=args.interval)
    
    if args.daemon:
        monitor.run_daemon()
    else:
        monitor.run_once()


if __name__ == "__main__":
    main()
