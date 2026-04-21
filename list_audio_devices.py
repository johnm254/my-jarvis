import sounddevice as sd
devices = sd.query_devices()
print("\nAvailable audio devices:\n")
for i, d in enumerate(devices):
    marker = ""
    if d["max_input_channels"] > 0:
        marker += " [MIC]"
    if d["max_output_channels"] > 0:
        marker += " [SPEAKER]"
    print(f"  [{i}] {d['name']}{marker}")

print(f"\nDefault input device:  [{sd.default.device[0]}] {devices[sd.default.device[0]]['name']}")
print(f"Default output device: [{sd.default.device[1]}] {devices[sd.default.device[1]]['name']}")
print("\nTo use your pods, set AUDIO_INPUT_DEVICE=<number> in .env")
