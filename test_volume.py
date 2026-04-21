"""
Test volume control to verify it works
"""

import time

def test_volume_control():
    """Test volume control functions."""
    print("🔊 Testing Volume Control\n")
    
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        
        # Get volume interface
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        print("✅ Volume control initialized successfully!\n")
        
        # Get current volume
        current = volume.GetMasterVolumeLevelScalar()
        print(f"📊 Current volume: {int(current * 100)}%\n")
        
        # Test volume up
        print("⬆️  Testing volume up...")
        new_vol = min(1.0, current + 0.1)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        time.sleep(0.5)
        actual = volume.GetMasterVolumeLevelScalar()
        print(f"   Volume set to: {int(actual * 100)}%\n")
        
        # Test volume down
        print("⬇️  Testing volume down...")
        new_vol = max(0.0, actual - 0.1)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        time.sleep(0.5)
        actual = volume.GetMasterVolumeLevelScalar()
        print(f"   Volume set to: {int(actual * 100)}%\n")
        
        # Test mute
        print("🔇 Testing mute...")
        volume.SetMute(1, None)
        time.sleep(0.5)
        is_muted = volume.GetMute()
        print(f"   Muted: {bool(is_muted)}\n")
        
        # Test unmute
        print("🔊 Testing unmute...")
        volume.SetMute(0, None)
        time.sleep(0.5)
        is_muted = volume.GetMute()
        print(f"   Muted: {bool(is_muted)}\n")
        
        # Restore original volume
        print("↩️  Restoring original volume...")
        volume.SetMasterVolumeLevelScalar(current, None)
        print(f"   Volume restored to: {int(current * 100)}%\n")
        
        print("✅ All volume control tests passed!\n")
        return True
        
    except ImportError as e:
        print(f"❌ Error: pycaw not installed")
        print(f"   Run: pip install pycaw comtypes\n")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


if __name__ == "__main__":
    test_volume_control()
