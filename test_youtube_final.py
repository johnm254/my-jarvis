"""
Test YouTube with tab management
"""

from jarvis.skills.music_player import MusicPlayerSkill
import time

print("🎵 Testing YouTube with Tab Management\n")

music = MusicPlayerSkill()

# Play first song
print("1️⃣  Playing first song: Despacito")
result = music.execute(action="play", query="Despacito")
if result.success:
    print(f"   ✅ {result.result}\n")
else:
    print(f"   ❌ Error: {result.error_message}\n")

print("⏳ Waiting 15 seconds for video to load and start...\n")
time.sleep(15)

# Play second song (should close first tab and open new one)
print("2️⃣  Playing second song: Shape of You")
result = music.execute(action="play", query="Shape of You")
if result.success:
    print(f"   ✅ {result.result}\n")
else:
    print(f"   ❌ Error: {result.error_message}\n")

print("✅ Test complete!")
print("   Check your browser - should have closed first tab and opened new one!\n")
print("   Net result: Only ONE YouTube tab!\n")
