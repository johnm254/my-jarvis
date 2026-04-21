"""Quick test to verify email notifications work."""
from dotenv import load_dotenv
load_dotenv()
import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from_email = os.getenv("NOTIFICATION_EMAIL", "")
password = os.getenv("NOTIFICATION_EMAIL_PASSWORD", "")

if not from_email or "your_" in from_email:
    print("❌  NOTIFICATION_EMAIL not set in .env"); exit(1)
if not password or "your_" in password:
    print("❌  NOTIFICATION_EMAIL_PASSWORD not set in .env"); exit(1)

print(f"📧  Sending test email from: {from_email}")

msg = MIMEMultipart()
msg["From"] = from_email
msg["To"] = from_email
msg["Subject"] = "JARVIS — Email Notifications Active"
msg.attach(MIMEText(
    "Good day, sir.\n\n"
    "JARVIS email notifications are configured and working correctly.\n\n"
    "I will notify you when tasks are completed.\n\n"
    "— JARVIS",
    "plain"
))

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(from_email, password)
        s.send_message(msg)
    print(f"✅  Test email sent to {from_email} — check your inbox!")
except smtplib.SMTPAuthenticationError:
    print("❌  Authentication failed.")
    print("    Make sure you're using a Gmail App Password, not your regular password.")
    print("    Get one at: https://myaccount.google.com/apppasswords")
except Exception as e:
    print(f"❌  Error: {e}")
