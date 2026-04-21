"""System Tools skill — gives JARVIS full access to the machine."""

import os
import shutil
import platform
import subprocess
import webbrowser
from datetime import datetime
from typing import Any

from jarvis.skills.base import Skill, SkillResult


class SystemToolsSkill(Skill):
    """
    Full system control: open apps/files/URLs, manage files, screenshots,
    clipboard, terminal commands, camera, running processes, system info.
    """

    # Common app name → command mapping
    _APP_MAP = {
        "vscode": "code",
        "code": "code",
        "vs code": "code",
        "visual studio code": "code",
        "explorer": "explorer",
        "file manager": "explorer",
        "file explorer": "explorer",
        "chrome": "chrome",
        "google chrome": "chrome",
        "notepad": "notepad",
        "terminal": "cmd",
        "cmd": "cmd",
        "command prompt": "cmd",
        "powershell": "powershell",
        "browser": None,  # handled specially
        "calculator": "calc",
        "paint": "mspaint",
        "word": "winword",
        "excel": "excel",
        "powerpoint": "powerpnt",
        "outlook": "outlook",
        "teams": "teams",
        "spotify": "spotify",
        "discord": "discord",
        "slack": "slack",
        "zoom": "zoom",
        "task manager": "taskmgr",
        "settings": "ms-settings:",
        "control panel": "control",
    }

    def __init__(self):
        super().__init__()
        self._name = "system_tools"
        self._description = (
            "Full system control: open apps, files, URLs, take screenshots, "
            "run terminal commands, manage files, access clipboard, camera, "
            "list/kill running processes, and get system info."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": (
                        "The system action to perform. Options: "
                        "open_app (open an application by name), "
                        "open_file (open a file), "
                        "open_url (open a URL in browser), "
                        "list_files (list files in a directory), "
                        "create_folder (create a new folder), "
                        "delete_file (delete a file or folder), "
                        "move_file (move a file), "
                        "copy_file (copy a file), "
                        "take_screenshot (capture the screen), "
                        "get_clipboard (read clipboard), "
                        "set_clipboard (write to clipboard), "
                        "run_terminal_command (run a shell command), "
                        "open_camera (open camera app), "
                        "list_running_apps (list running processes), "
                        "kill_app (terminate an application), "
                        "get_system_info (get CPU/RAM/disk info)"
                    ),
                },
                "target": {
                    "type": "string",
                    "description": "App name, file path, URL, command, or text depending on action.",
                },
                "destination": {
                    "type": "string",
                    "description": "Destination path for move/copy operations.",
                },
            },
            "required": ["action"],
        }

    def execute(self, **kwargs) -> SkillResult:
        action = kwargs.get("action", "")
        target = kwargs.get("target", "")
        destination = kwargs.get("destination", "")

        try:
            handler = getattr(self, f"_action_{action}", None)
            if handler is None:
                return SkillResult(success=False, result=None,
                                   error_message=f"Unknown action: {action}")
            return handler(target=target, destination=destination)
        except Exception as e:
            return SkillResult(success=False, result=None,
                               error_message=str(e))

    # ── Action handlers ────────────────────────────────────────────────────────

    def _action_open_app(self, target: str, **_) -> SkillResult:
        name = target.lower().strip()
        cmd = self._APP_MAP.get(name)

        if cmd is None and name in ("browser",):
            webbrowser.open("https://www.google.com")
            return SkillResult(success=True, result="Opened default browser.")

        if cmd is None:
            cmd = target  # try running the name directly

        try:
            if cmd.startswith("ms-"):
                # Windows URI scheme (e.g. ms-settings:)
                subprocess.Popen(["start", "", cmd], shell=True)
            elif cmd in ("explorer",):
                subprocess.Popen("explorer", shell=True)
            elif cmd in ("cmd",):
                subprocess.Popen("start cmd", shell=True)
            elif cmd in ("powershell",):
                subprocess.Popen("start powershell", shell=True)
            else:
                # Use 'start' to launch by name — Windows resolves PATH apps
                subprocess.Popen(f'start "" "{cmd}"', shell=True)
            return SkillResult(success=True, result=f"Opened '{target}'.")
        except Exception as e:
            return SkillResult(success=False, result=None,
                               error_message=f"Could not open '{target}': {e}")

    def _action_open_file(self, target: str, **_) -> SkillResult:
        if not target:
            return SkillResult(success=False, result=None,
                               error_message="No file path provided.")
        if platform.system() == "Windows":
            os.startfile(target)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", target])
        else:
            subprocess.Popen(["xdg-open", target])
        return SkillResult(success=True, result=f"Opened file: {target}")

    def _action_open_url(self, target: str, **_) -> SkillResult:
        if not target:
            return SkillResult(success=False, result=None,
                               error_message="No URL provided.")
        if not target.startswith(("http://", "https://")):
            target = "https://" + target
        webbrowser.open(target)
        return SkillResult(success=True, result=f"Opened URL: {target}")

    def _action_list_files(self, target: str, **_) -> SkillResult:
        path = target or os.getcwd()
        try:
            files = os.listdir(path)
            return SkillResult(success=True, result={"path": path, "files": files})
        except Exception as e:
            return SkillResult(success=False, result=None, error_message=str(e))

    def _action_create_folder(self, target: str, **_) -> SkillResult:
        if not target:
            return SkillResult(success=False, result=None,
                               error_message="No folder path provided.")
        os.makedirs(target, exist_ok=True)
        return SkillResult(success=True, result=f"Folder created: {target}")

    def _action_delete_file(self, target: str, **_) -> SkillResult:
        if not target:
            return SkillResult(success=False, result=None,
                               error_message="No path provided.")
        if os.path.isdir(target):
            shutil.rmtree(target)
        else:
            os.remove(target)
        return SkillResult(success=True, result=f"Deleted: {target}")

    def _action_move_file(self, target: str, destination: str, **_) -> SkillResult:
        if not target or not destination:
            return SkillResult(success=False, result=None,
                               error_message="Both target and destination are required.")
        shutil.move(target, destination)
        return SkillResult(success=True, result=f"Moved '{target}' → '{destination}'")

    def _action_copy_file(self, target: str, destination: str, **_) -> SkillResult:
        if not target or not destination:
            return SkillResult(success=False, result=None,
                               error_message="Both target and destination are required.")
        shutil.copy2(target, destination)
        return SkillResult(success=True, result=f"Copied '{target}' → '{destination}'")

    def _action_take_screenshot(self, **_) -> SkillResult:
        out_dir = os.path.join("jarvis_output", "screenshots")
        os.makedirs(out_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(out_dir, f"screenshot_{timestamp}.png")

        # Try PIL first (silent, saves directly)
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            img.save(out_path)
            return SkillResult(success=True, result=f"Screenshot saved: {out_path}")
        except ImportError:
            pass

        # Fallback: Snipping Tool (Windows)
        subprocess.run(["snippingtool"], shell=True)
        return SkillResult(success=True,
                           result="Snipping Tool opened. Save your screenshot manually.")

    def _action_get_clipboard(self, **_) -> SkillResult:
        result = subprocess.run(
            ["powershell", "-command", "Get-Clipboard"],
            capture_output=True, text=True
        )
        text = result.stdout.strip()
        return SkillResult(success=True, result={"clipboard": text})

    def _action_set_clipboard(self, target: str, **_) -> SkillResult:
        if not target:
            return SkillResult(success=False, result=None,
                               error_message="No text provided for clipboard.")
        # Escape single quotes
        safe = target.replace("'", "''")
        subprocess.run(
            ["powershell", "-command", f"Set-Clipboard '{safe}'"],
            capture_output=True
        )
        return SkillResult(success=True, result="Clipboard updated.")

    def _action_run_terminal_command(self, target: str, **_) -> SkillResult:
        if not target:
            return SkillResult(success=False, result=None,
                               error_message="No command provided.")
        result = subprocess.run(
            target, shell=True, capture_output=True, text=True, timeout=30
        )
        return SkillResult(success=True, result={
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        })

    def _action_open_camera(self, **_) -> SkillResult:
        subprocess.Popen(["start", "microsoft.windows.camera:"], shell=True)
        return SkillResult(success=True, result="Camera app opened.")

    def _action_list_running_apps(self, **_) -> SkillResult:
        result = subprocess.run(
            ["tasklist"], capture_output=True, text=True
        )
        lines = [l for l in result.stdout.splitlines() if l.strip()]
        return SkillResult(success=True, result={"processes": lines})

    def _action_kill_app(self, target: str, **_) -> SkillResult:
        if not target:
            return SkillResult(success=False, result=None,
                               error_message="No app name provided.")
        # Ensure .exe suffix
        if not target.lower().endswith(".exe"):
            target = target + ".exe"
        result = subprocess.run(
            ["taskkill", "/F", "/IM", target], capture_output=True, text=True
        )
        success = result.returncode == 0
        return SkillResult(
            success=success,
            result=result.stdout.strip() or result.stderr.strip(),
            error_message=None if success else result.stderr.strip(),
        )

    def _action_get_system_info(self, **_) -> SkillResult:
        info: dict[str, Any] = {
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "hostname": platform.node(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }

        try:
            import getpass
            info["username"] = getpass.getuser()
        except Exception:
            pass

        try:
            import psutil
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            info["cpu_count"] = psutil.cpu_count(logical=True)
            info["cpu_percent"] = psutil.cpu_percent(interval=0.5)
            info["ram_total_gb"] = round(mem.total / 1e9, 2)
            info["ram_used_gb"] = round(mem.used / 1e9, 2)
            info["ram_percent"] = mem.percent
            info["disk_total_gb"] = round(disk.total / 1e9, 2)
            info["disk_used_gb"] = round(disk.used / 1e9, 2)
            info["disk_percent"] = disk.percent
        except ImportError:
            info["note"] = "Install psutil for CPU/RAM/disk details."

        return SkillResult(success=True, result=info)
