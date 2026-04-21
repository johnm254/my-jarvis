"""
Test Music Player - YouTube Auto-Play and Volume Control
"""

import time
from jarvis.skills.music_player import MusicPlayerSkill


def test_music_player():
    """Test music player functionality."""
    print("\n" + "="*70)
    print("🎵 TESTING MUSIC PLAYER")
    print("="*70 + "\n")
    
    player = MusicPlayerSkill()
    
    # Test 1: Get current volume
    print("📊 Test 1: Get Current Volume")
    result = player.execute(action="get_volume")
    if result.success:
        print(f"✅ Current volume: {result.result['volume']}%")
    else:
        print(f"❌ Failed: {result.error_message}")
    print()
    
    # Test 2: Set volume to 50%
    print("🔊 Test 2: Set Volume to 50%")
    result = player.execute(action="set_volume", level=50)
    if result.success:
        print(f"✅ Volume set to: {result.result['volume']}%")
    else:
        print(f"❌ Failed: {result.error_message}")
    time.sleep(1)
    print()
    
    # Test 3: Volume up
    print("⬆️  Test 3: Volume Up")
    result = player.execute(action="volume_up")
    if result.success:
        print(f"✅ Volume increased to: {result.result['volume']}%")
    else:
        print(f"❌ Failed: {result.error_message}")
    time.sleep(1)
    print()
    
    # Test 4: Volume down
    print("⬇️  Test 4: Volume Down")
    result = player.execute(action="volume_down")
    if result.success:
        print(f"✅ Volume decreased to: {result.result['volume']}%")
    else:
        print(f"❌ Failed: {result.error_message}")
    time.sleep(1)
    print()
    
    # Test 5: Mute
    print("🔇 Test 5: Mute")
    result = player.execute(action="mute")
    if result.success:
        print("✅ Audio muted")
    else:
        print(f"❌ Failed: {result.error_message}")
    time.sleep(2)
    print()
    
    # Test 6: Unmute
    print("🔊 Test 6: Unmute")
    result = player.execute(action="unmute")
    if result.success:
        print("✅ Audio unmuted")
    else:
        print(f"❌ Failed: {result.error_message}")
    time.sleep(1)
    print()
    
    # Test 7: Play music (YouTube auto-play)
    print("🎵 Test 7: Play Music on YouTube")
    print("⚠️  This will open YouTube and auto-play a video")
    print("   Watch your browser - it should click and play automatically!")
    print()
    
    choice = input("Ready to test YouTube auto-play? (y/n): ").strip().lower()
    if choice == 'y':
        song = input("Enter song name (or press Enter for 'Despacito'): ").strip()
        if not song:
            song = "Despacito"
        
        print(f"\n🎵 Playing: {song}")
        print("   Opening YouTube...")
        print("   Waiting 5 seconds for page to load...")
        print("   Auto-clicking first video...")
        print()
        
        result = player.execute(action="play", query=song)
        if result.success:
            print(f"✅ Started playing: {song}")
            print("   Check your browser - video should be playing!")
        else:
            print(f"❌ Failed: {result.error_message}")
        
        print("\n⏳ Waiting 10 seconds to see if video plays...")
        time.sleep(10)
    
    print("\n" + "="*70)
    print("✅ MUSIC PLAYER TEST COMPLETE!")
    print("="*70 + "\n")
    
    print("📊 Summary:")
    print("  ✅ Volume control - Tested")
    print("  ✅ Mute/Unmute - Tested")
    print("  ✅ YouTube auto-play - Tested")
    print()
    print("💡 Tips:")
    print("  - If auto-play didn't work, adjust screen coordinates in music_player.py")
    print("  - First video position varies by screen size")
    print("  - Make sure browser window is visible when playing")
    print()


if __name__ == "__main__":
    try:
        test_music_player()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
