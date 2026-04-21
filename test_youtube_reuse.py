"""
Test YouTube tab reuse
"""

from jarvis.skills.music_player import MusicPlayerSkill
import time

print("🎵 Testing YouTube Tab Reuse\n")

music = MusicPlayerSkill()

# Play first song
print("1️⃣  Playing first song: Despacito")
result = music.execute(action="play", query="Despacito")
if result.success:
    print(f"   ✅ Playing: {result.result['playing']}\n")
else:
    print(f"   ❌ Error: {result.error_message}\n")

# Wait for video to start
print("⏳ Waiting 10 seconds for video to start...\n")
time.sleep(10)

# Play second song (should reuse same tab)
print("2️⃣  Playing second song: Shape of You")
result = music.execute(action="play", query="Shape of You")
if result.success:
    print(f"   ✅ Playing: {result.result['playing']}\n")
else:
    print(f"   ❌ Error: {result.error_message}\n")

print("✅ Test complete!")
print("   Check your browser - should only have ONE YouTube tab!\n")
