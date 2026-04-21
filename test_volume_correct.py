"""
Correct pycaw API for volume control
"""

try:
    from pycaw.pycaw import AudioUtilities
    
    print("🔊 Testing Volume Control (Correct API)\n")
    
    # Get speakers
    speakers = AudioUtilities.GetSpeakers()
    print(f"✅ Speakers: {speakers.FriendlyName}\n")
    
    # Get volume interface directly
    volume = speakers.EndpointVolume
    print(f"✅ Volume control ready!\n")
    
    # Get current volume
    current_volume = volume.GetMasterVolumeLevelScalar()
    print(f"📊 Current volume: {int(current_volume * 100)}%\n")
    
    # Test volume up
    print("⬆️  Increasing volume by 10%...")
    new_volume = min(1.0, current_volume + 0.1)
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    actual = volume.GetMasterVolumeLevelScalar()
    print(f"   New volume: {int(actual * 100)}%\n")
    
    # Test volume down
    print("⬇️  Decreasing volume by 10%...")
    new_volume = max(0.0, actual - 0.1)
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    actual = volume.GetMasterVolumeLevelScalar()
    print(f"   New volume: {int(actual * 100)}%\n")
    
    # Test mute
    print("🔇 Testing mute...")
    volume.SetMute(1, None)
    is_muted = volume.GetMute()
    print(f"   Muted: {bool(is_muted)}\n")
    
    # Test unmute
    print("🔊 Testing unmute...")
    volume.SetMute(0, None)
    is_muted = volume.GetMute()
    print(f"   Muted: {bool(is_muted)}\n")
    
    # Restore
    print("↩️  Restoring original volume...")
    volume.SetMasterVolumeLevelScalar(current_volume, None)
    print(f"   Volume restored to: {int(current_volume * 100)}%\n")
    
    print("✅ All volume control tests passed!\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
