from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
current = volume.GetMasterVolumeLevelScalar()
print(f"Current volume: {int(current * 100)}%")

# Test set to 50%
volume.SetMasterVolumeLevelScalar(0.5, None)
print("Set to 50%")
import time; time.sleep(1)
# Restore
volume.SetMasterVolumeLevelScalar(current, None)
print(f"Restored to {int(current * 100)}%")
