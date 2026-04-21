import subprocess, time, os

# Test opening apps
tests = [
    ("notepad", 'start "" "notepad"'),
    ("explorer", 'start "" "explorer"'),
    ("chrome", 'start "" "chrome"'),
]

for name, cmd in tests:
    print(f"Testing: {name}")
    try:
        subprocess.Popen(cmd, shell=True)
        time.sleep(1)
        print(f"  ✅ {name} opened")
    except Exception as e:
        print(f"  ❌ {name} failed: {e}")
