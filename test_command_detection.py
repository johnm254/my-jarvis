"""
Test command detection and execution
"""

from conversational_jarvis import ConversationalJARVIS
import time

print("🧪 Testing Command Detection and Execution\n")

# Initialize JARVIS
jarvis = ConversationalJARVIS(voice_enabled=False)

print("📧 Testing email commands...")
test_commands = [
    "send me email test message",
    "email me hello",
    "send it now",
    "is it in my email"
]

for cmd in test_commands:
    print(f"\n   Testing: '{cmd}'")
    jarvis.handle_conversation(cmd)
    time.sleep(1)

print("\n🎵 Testing music commands...")
music_commands = [
    "play despacito",
    "play another song",
    "play shape of you"
]

for cmd in music_commands:
    print(f"\n   Testing: '{cmd}'")
    jarvis.handle_conversation(cmd)
    time.sleep(1)

print("\n✅ Command detection test complete!")
print("   Check if:")
print("   - Email commands actually send emails")
print("   - Music commands actually open YouTube")
print("   - No fake responses about actions not taken\n")