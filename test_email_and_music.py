"""
Test email and music functionality
"""

print("📧 Testing Email Functionality\n")

# Test email directly
from jarvis.skills.email_notifier import EmailNotifierSkill

email_skill = EmailNotifierSkill()

print("🔧 Testing email skill directly...")
result = email_skill.execute(
    to="johnmwangi1729@gmail.com",
    subject="JARVIS Test Email",
    body="This is a test email from JARVIS to verify email functionality is working."
)

if result.success:
    print(f"✅ Email skill says: {result.result}")
else:
    print(f"❌ Email skill failed: {result.error_message}")

print("\n🎵 Testing Music Functionality\n")

# Test music directly
from jarvis.skills.music_player import MusicPlayerSkill

music_skill = MusicPlayerSkill()

print("🔧 Testing music skill directly...")
result = music_skill.execute(action="play", query="Despacito")

if result.success:
    print(f"✅ Music skill says: {result.result}")
    print("   Check your browser - did YouTube open?")
else:
    print(f"❌ Music skill failed: {result.error_message}")

print("\n✅ Direct skill tests complete!")
print("   Check if email arrived and if YouTube opened\n")