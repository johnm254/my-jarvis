"""
Simple volume control test with correct pycaw API
"""

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    
    print("🔊 Testing Volume Control\n")
    
    # Get default audio device
    devices = AudioUtilities.GetSpeakers()
    print(f"✅ Found audio device: {devices}\n")
    
    # Get the interface
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    print(f"✅ Got interface: {interface}\n")
    
    # Cast to volume control
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
    print(f"   Type: {type(e)}")
    import traceback
    traceback.print_exc()
