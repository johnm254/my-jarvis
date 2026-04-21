"""
Modern pycaw API for volume control
"""

try:
    from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
    
    print("🔊 Testing Volume Control (Modern API)\n")
    
    # Get all sessions
    sessions = AudioUtilities.GetAllSessions()
    print(f"✅ Found {len(sessions)} audio sessions\n")
    
    # Try to control system volume using a different approach
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import IAudioEndpointVolume
    
    # Get speakers
    speakers = AudioUtilities.GetSpeakers()
    print(f"✅ Speakers: {speakers}\n")
    
    # Try to get the interface directly from the device
    from pycaw.utils import AudioDevice
    
    # Alternative: Use the device's IMMDevice interface
    interface = speakers.device.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    
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
    
    # Restore
    print("↩️  Restoring original volume...")
    volume.SetMasterVolumeLevelScalar(current_volume, None)
    print(f"   Volume restored to: {int(current_volume * 100)}%\n")
    
    print("✅ Volume control works!\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
