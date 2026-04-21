"""
Test environment variable loading
"""

import os
from dotenv import load_dotenv

print("🔧 Testing Environment Variable Loading\n")

# Load .env file
load_dotenv()

# Check email variables
notification_email = os.getenv("NOTIFICATION_EMAIL")
notification_password = os.getenv("NOTIFICATION_EMAIL_PASSWORD")

print(f"📧 NOTIFICATION_EMAIL: {notification_email}")
print(f"🔑 NOTIFICATION_EMAIL_PASSWORD: {'*' * len(notification_password) if notification_password else 'None'}")

if notification_email and notification_password:
    print("✅ Email configuration loaded successfully!")
    
    # Test email with proper loading
    from jarvis.skills.email_notifier import EmailNotifierSkill
    
    email_skill = EmailNotifierSkill()
    result = email_skill.execute(
        to="johnmwangi1729@gmail.com",
        subject="JARVIS Test - Environment Loading",
        body="This email tests if environment variables are loading correctly."
    )
    
    if result.success:
        print(f"✅ Email sent: {result.result}")
    else:
        print(f"❌ Email failed: {result.error_message}")
        
else:
    print("❌ Email configuration not loaded!")

print("\n🎵 Testing YouTube opening...")

import webbrowser
import time

try:
    webbrowser.open("https://www.youtube.com/results?search_query=Despacito")
    print("✅ YouTube should have opened in your browser")
    print("   Check if a new tab/window opened with YouTube search")
except Exception as e:
    print(f"❌ Failed to open YouTube: {e}")

print("\n✅ Environment and basic functionality test complete!")