"""
Add JARVIS to Windows startup so it launches automatically when you log in.
Run once: python setup_autostart.py
"""
import os
import sys
import winreg

# Path to this project and Python
project_dir = os.path.abspath(os.path.dirname(__file__))
python_exe = sys.executable
script = os.path.join(project_dir, "jarvis_voice.py")

# Create a .bat launcher that runs minimized in background
bat_path = os.path.join(project_dir, "start_jarvis.bat")
bat_content = f"""@echo off
cd /d "{project_dir}"
start "" /min "{python_exe}" "{script}"
"""
with open(bat_path, "w") as f:
    f.write(bat_content)
print(f"✅  Created launcher: {bat_path}")

# Add to Windows Registry startup
key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "JARVIS", 0, winreg.REG_SZ, bat_path)
    winreg.CloseKey(key)
    print("✅  JARVIS added to Windows startup")
    print("   JARVIS will now start automatically when you log in.")
    print(f"\n   To remove: run  python setup_autostart.py --remove")
except Exception as e:
    print(f"❌  Failed to add to registry: {e}")
    # Fallback: add to Startup folder
    startup_folder = os.path.join(
        os.environ.get("APPDATA", ""),
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )
    import shutil
    dest = os.path.join(startup_folder, "start_jarvis.bat")
    shutil.copy(bat_path, dest)
    print(f"✅  Added to Startup folder instead: {dest}")

if "--remove" in sys.argv:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "JARVIS")
        winreg.CloseKey(key)
        print("✅  JARVIS removed from startup")
    except Exception as e:
        print(f"❌  {e}")
