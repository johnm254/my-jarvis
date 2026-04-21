"""
Test YouTube playback to ensure videos actually play
"""

from jarvis.skills.music_player import MusicPlayerSkill
import time

print("🎵 Testing YouTube Playback\n")

music = MusicPlayerSkill()

print("🎬 Testing YouTube video playback...")
print("   This will open YouTube and attempt to play a video")
print("   Watch your browser to see if the video actually starts playing!\n")

# Test playing a song
result = music.execute(action="play", query="Despacito")

if result.success:
    print(f"✅ JARVIS says: {result.result}")
    print("\n🔍 Check your browser:")
    print("   1. Did YouTube open? ✅")
    print("   2. Did it search for 'Despacito'? ✅") 
    print("   3. Did it click on the first video? 🔍")
    print("   4. Is the video actually PLAYING? 🔍")
    print("\n⏳ Waiting 10 seconds for you to check...")
    
    for i in range(10, 0, -1):
        print(f"   {i} seconds remaining...", end='\r')
        time.sleep(1)
    
    print("\n\n💬 Did the video actually play?")
    print("   If YES: YouTube playback is working! ✅")
    print("   If NO: The video loaded but didn't auto-play ❌")
    
else:
    print(f"❌ JARVIS failed: {result.error_message}")

print("\n✅ Test complete!")
print("   Please report if the video played or just loaded\n")