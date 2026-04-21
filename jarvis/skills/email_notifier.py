"""Email Notifier skill — send email notifications via SMTP."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from jarvis.skills.base import Skill, SkillResult


class EmailNotifierSkill(Skill):
    """
    Send email notifications using SMTP (Gmail by default).
    Requires NOTIFICATION_EMAIL and NOTIFICATION_EMAIL_PASSWORD env vars.
    """

    def __init__(self):
        super().__init__()
        self._name = "send_email"
        self._description = (
            "Send email notifications. Useful for notifying when tasks complete "
            "or sending reports/summaries."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email address.",
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject line.",
                },
                "body": {
                    "type": "string",
                    "description": "Email body content (plain text).",
                },
            },
            "required": ["to", "subject", "body"],
        }

    def execute(self, **kwargs) -> SkillResult:
        to_email = kwargs.get("to", "")
        subject = kwargs.get("subject", "")
        body = kwargs.get("body", "")
        # Always use env vars for credentials — never trust what the brain passes
        from_email = os.getenv("NOTIFICATION_EMAIL", "")
        smtp_password = os.getenv("NOTIFICATION_EMAIL_PASSWORD", "")

        # Validate configuration
        if not from_email or not smtp_password:
            return SkillResult(
                success=False,
                result=None,
                error_message=(
                    "Email not configured. Please set NOTIFICATION_EMAIL and "
                    "NOTIFICATION_EMAIL_PASSWORD in your .env file. "
                    "For Gmail, use an App Password: "
                    "https://support.google.com/accounts/answer/185833"
                ),
            )

        if not to_email or not subject or not body:
            return SkillResult(
                success=False,
                result=None,
                error_message="Missing required fields: to, subject, or body.",
            )

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = from_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            # Connect to Gmail SMTP
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(from_email, smtp_password)
                server.send_message(msg)

            return SkillResult(
                success=True,
                result=f"Email sent to {to_email}",
            )

        except smtplib.SMTPAuthenticationError:
            return SkillResult(
                success=False,
                result=None,
                error_message=(
                    "SMTP authentication failed. For Gmail, ensure you're using an "
                    "App Password (not your regular password): "
                    "https://support.google.com/accounts/answer/185833"
                ),
            )
        except Exception as e:
            return SkillResult(
                success=False,
                result=None,
                error_message=f"Failed to send email: {str(e)}",
            )
