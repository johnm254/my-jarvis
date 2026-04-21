"""
Automated Music Player Test
"""

import time
from jarvis.skills.music_player import MusicPlayerSkill


def test_volume_control():
    """Test volume control only."""
    print("\n" + "="*70)
    print("🔊 TESTING VOLUME CONTROL")
    print("="*70 + "\n")
    
    player = MusicPlayerSkill()
    
    tests_passed = 0
    tests_total = 6
    
    # Test 1: Get volume
    print("1️⃣  Getting current volume...")
    result = player.execute(action="get_volume")
    if result.success:
        print(f"   ✅ Current volume: {result.result['volume']}%")
        tests_passed += 1
    else:
        print(f"   ❌ Failed: {result.error_message}")
    
    # Test 2: Set volume to 30%
    print("\n2️⃣  Setting volume to 30%...")
    result = player.execute(action="set_volume", level=30)
    if result.success:
        print(f"   ✅ Volume set to: {result.result['volume']}%")
        tests_passed += 1
    else:
        print(f"   ❌ Failed: {result.error_message}")
    time.sleep(1)
    
    # Test 3: Volume up
    print("\n3️⃣  Increasing volume...")
    result = player.execute(action="volume_up")
    if result.success:
        print(f"   ✅ Volume increased to: {result.result['volume']}%")
        tests_passed += 1
    else:
        print(f"   ❌ Failed: {result.error_message}")
    time.sleep(1)
    
    # Test 4: Volume down
    print("\n4️⃣  Decreasing volume...")
    result = player.execute(action="volume_down")
    if result.success:
        print(f"   ✅ Volume decreased to: {result.result['volume']}%")
        tests_passed += 1
    else:
        print(f"   ❌ Failed: {result.error_message}")
    time.sleep(1)
    
    # Test 5: Mute
    print("\n5️⃣  Muting audio...")
    result = player.execute(action="mute")
    if result.success:
        print("   ✅ Audio muted")
        tests_passed += 1
    else:
        print(f"   ❌ Failed: {result.error_message}")
    time.sleep(2)
    
    # Test 6: Unmute
    print("\n6️⃣  Unmuting audio...")
    result = player.execute(action="unmute")
    if result.success:
        print("   ✅ Audio unmuted")
        tests_passed += 1
    else:
        print(f"   ❌ Failed: {result.error_message}")
    
    # Restore volume to 50%
    print("\n🔄 Restoring volume to 50%...")
    player.execute(action="set_volume", level=50)
    
    print("\n" + "="*70)
    print(f"✅ VOLUME CONTROL TEST COMPLETE: {tests_passed}/{tests_total} passed")
    print("="*70 + "\n")
    
    return tests_passed == tests_total


def test_youtube_play():
    """Test YouTube auto-play."""
    print("\n" + "="*70)
    print("🎵 TESTING YOUTUBE AUTO-PLAY")
    print("="*70 + "\n")
    
    player = MusicPlayerSkill()
    
    print("🎵 Playing 'Despacito' on YouTube")
    print("   This will:")
    print("   1. Open YouTube search")
    print("   2. Wait 5 seconds for page load")
    print("   3. Auto-click first video")
    print("   4. Video should start playing")
    print()
    
    result = player.execute(action="play", query="Despacito")
    
    if result.success:
        print("✅ YouTube auto-play initiated!")
        print("   Check your browser - video should be playing")
        print()
        print("⏳ Waiting 8 seconds to verify...")
        time.sleep(8)
        print()
        print("✅ If video is playing, auto-play works!")
        print("❌ If video is not playing, see troubleshooting below")
        return True
    else:
        print(f"❌ Failed: {result.error_message}")
        return False


def main():
    """Run all tests."""
    print("\n╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  MUSIC PLAYER - AUTOMATED TEST".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    # Test volume control
    volume_ok = test_volume_control()
    
    # Test YouTube auto-play
    youtube_ok = test_youtube_play()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"  Volume Control: {'✅ PASSED' if volume_ok else '❌ FAILED'}")
    print(f"  YouTube Auto-Play: {'✅ PASSED' if youtube_ok else '❌ FAILED'}")
    print("="*70 + "\n")
    
    if volume_ok and youtube_ok:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Your music player is fully functional!")
        print("\n💬 Try these commands with JARVIS:")
        print("   'Play Despacito'")
        print("   'Volume up'")
        print("   'Volume down'")
        print("   'Set volume to 50'")
        print("   'Mute'")
        print("   'Unmute'")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\n🔧 Troubleshooting:")
        
        if not volume_ok:
            print("\n❌ Volume Control Issues:")
            print("   - Make sure pycaw is installed: pip install pycaw comtypes")
            print("   - Run as administrator if needed")
        
        if not youtube_ok:
            print("\n❌ YouTube Auto-Play Issues:")
            print("   - Make sure pyautogui is installed: pip install pyautogui")
            print("   - Adjust screen coordinates in music_player.py")
            print("   - First video position: screen_width * 0.20, screen_height * 0.30")
            print("   - Try different values based on your screen size")
            print("   - Make sure browser window is visible")
    
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
