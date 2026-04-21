"""
Test JARVIS conversational functionality directly
"""

from conversational_jarvis import ConversationalJARVIS
import os

print("🤖 Testing JARVIS Conversational Functionality\n")

# Initialize JARVIS
jarvis = ConversationalJARVIS(voice_enabled=False)

print("📧 Testing email command...")
print("   Simulating: 'send me email test message'\n")

# Test email command directly
jarvis.handle_conversation("send me email test message")

print("\n🎵 Testing music command...")
print("   Simulating: 'play despacito'\n")

# Test music command directly
jarvis.handle_conversation("play despacito")

print("\n✅ Direct JARVIS test complete!")
print("   Check if email was sent and if YouTube opened\n")

# Also test environment variables
print("🔧 Environment check:")
print(f"   NOTIFICATION_EMAIL: {os.getenv('NOTIFICATION_EMAIL', 'NOT SET')}")
print(f"   LLM_API_KEY: {'SET' if os.getenv('LLM_API_KEY') else 'NOT SET'}")