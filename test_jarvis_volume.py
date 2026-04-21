"""
Test JARVIS volume control
"""

from jarvis.skills.music_player import MusicPlayerSkill

print("🔊 Testing JARVIS Volume Control\n")

music = MusicPlayerSkill()

# Test get volume
print("📊 Getting current volume...")
result = music.execute(action="get_volume")
if result.success:
    print(f"   Current volume: {result.result['volume']}%\n")
else:
    print(f"   Error: {result.error_message}\n")

# Test volume up
print("⬆️  Testing volume up...")
result = music.execute(action="volume_up")
if result.success:
    print(f"   New volume: {result.result['volume']}%\n")
else:
    print(f"   Error: {result.error_message}\n")

# Test volume down
print("⬇️  Testing volume down...")
result = music.execute(action="volume_down")
if result.success:
    print(f"   New volume: {result.result['volume']}%\n")
else:
    print(f"   Error: {result.error_message}\n")

# Test set volume
print("🎚️  Testing set volume to 50...")
result = music.execute(action="set_volume", level=50)
if result.success:
    print(f"   Volume set to: {result.result['volume']}%\n")
else:
    print(f"   Error: {result.error_message}\n")

# Test mute
print("🔇 Testing mute...")
result = music.execute(action="mute")
if result.success:
    print(f"   Muted!\n")
else:
    print(f"   Error: {result.error_message}\n")

# Test unmute
print("🔊 Testing unmute...")
result = music.execute(action="unmute")
if result.success:
    print(f"   Unmuted!\n")
else:
    print(f"   Error: {result.error_message}\n")

print("✅ All JARVIS volume control tests completed!\n")
