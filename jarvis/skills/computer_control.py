"""
Computer Control Skill - Full keyboard, mouse, navigation, and typing control
JARVIS can control everything on your computer through voice commands
"""

import os
import time
import logging
import pyautogui
import subprocess
from pathlib import Path
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)

# Configure pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1


class ComputerControlSkill(Skill):
    """Complete computer control - keyboard, mouse, navigation, typing, file management."""
    
    def __init__(self):
        super().__init__()
        self._name = "computer_control"
        self._description = (
            "Full computer control: keyboard shortcuts, mouse clicks, navigation, "
            "typing text, opening files, searching files, window management, "
            "and complete system control through voice commands."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": (
                        "Action to perform: 'click', 'type', 'press_key', 'hotkey', "
                        "'move_mouse', 'scroll', 'search_file', 'open_file', "
                        "'navigate_to', 'switch_window', 'close_window', "
                        "'minimize', 'maximize', 'screenshot', 'find_on_screen'"
                    ),
                },
                "text": {"type": "string", "description": "Text to type"},
                "key": {"type": "string", "description": "Key to press"},
                "keys": {"type": "array", "description": "Keys for hotkey combination"},
                "x": {"type": "number", "description": "X coordinate"},
                "y": {"type": "number", "description": "Y coordinate"},
                "clicks": {"type": "number", "description": "Number of clicks"},
                "button": {"type": "string", "description": "Mouse button: left, right, middle"},
                "direction": {"type": "string", "description": "Scroll direction: up, down"},
                "amount": {"type": "number", "description": "Scroll amount"},
                "query": {"type": "string", "description": "Search query or file name"},
                "path": {"type": "string", "description": "File or folder path"},
            },
            "required": ["action"],
        }
    
    def execute(self, **kwargs) -> SkillResult:
        """Execute computer control action."""
        start = time.time()
        action = kwargs.get("action")
        
        try:
            if action == "click":
                result = self._click(**kwargs)
            elif action == "type":
                result = self._type_text(**kwargs)
            elif action == "press_key":
                result = self._press_key(**kwargs)
            elif action == "hotkey":
                result = self._hotkey(**kwargs)
            elif action == "move_mouse":
                result = self._move_mouse(**kwargs)
            elif action == "scroll":
                result = self._scroll(**kwargs)
            elif action == "search_file":
                result = self._search_file(**kwargs)
            elif action == "open_file":
                result = self._open_file(**kwargs)
            elif action == "navigate_to":
                result = self._navigate_to(**kwargs)
            elif action == "switch_window":
                result = self._switch_window(**kwargs)
            elif action == "close_window":
                result = self._close_window(**kwargs)
            elif action == "minimize":
                result = self._minimize(**kwargs)
            elif action == "maximize":
                result = self._maximize(**kwargs)
            elif action == "screenshot":
                result = self._screenshot(**kwargs)
            elif action == "find_on_screen":
                result = self._find_on_screen(**kwargs)
            else:
                return SkillResult(
                    success=False,
                    result=None,
                    error_message=f"Unknown action: {action}",
                    execution_time_ms=int((time.time() - start) * 1000)
                )
            
            return SkillResult(
                success=True,
                result=result,
                execution_time_ms=int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            logger.error(f"Computer control error: {e}")
            return SkillResult(
                success=False,
                result=None,
                error_message=str(e),
                execution_time_ms=int((time.time() - start) * 1000)
            )
    
    def _click(self, **kwargs):
        """Click mouse at position or current location."""
        x = kwargs.get("x")
        y = kwargs.get("y")
        clicks = kwargs.get("clicks", 1)
        button = kwargs.get("button", "left")
        
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, button=button)
            return {"clicked": True, "position": (x, y), "clicks": clicks}
        else:
            pyautogui.click(clicks=clicks, button=button)
            pos = pyautogui.position()
            return {"clicked": True, "position": (pos.x, pos.y), "clicks": clicks}
    
    def _type_text(self, **kwargs):
        """Type text."""
        text = kwargs.get("text", "")
        interval = kwargs.get("interval", 0.05)
        
        pyautogui.write(text, interval=interval)
        return {"typed": text, "length": len(text)}
    
    def _press_key(self, **kwargs):
        """Press a single key."""
        key = kwargs.get("key")
        presses = kwargs.get("presses", 1)
        
        if not key:
            return {"error": "No key specified"}
        
        pyautogui.press(key, presses=presses)
        return {"pressed": key, "presses": presses}
    
    def _hotkey(self, **kwargs):
        """Press hotkey combination."""
        keys = kwargs.get("keys", [])
        
        if not keys:
            return {"error": "No keys specified"}
        
        pyautogui.hotkey(*keys)
        return {"hotkey": "+".join(keys)}
    
    def _move_mouse(self, **kwargs):
        """Move mouse to position."""
        x = kwargs.get("x")
        y = kwargs.get("y")
        duration = kwargs.get("duration", 0.5)
        
        if x is None or y is None:
            return {"error": "X and Y coordinates required"}
        
        pyautogui.moveTo(x, y, duration=duration)
        return {"moved_to": (x, y)}
    
    def _scroll(self, **kwargs):
        """Scroll up or down."""
        direction = kwargs.get("direction", "down")
        amount = kwargs.get("amount", 3)
        
        scroll_amount = -amount if direction == "down" else amount
        pyautogui.scroll(scroll_amount * 100)
        return {"scrolled": direction, "amount": amount}
    
    def _search_file(self, **kwargs):
        """Search for files on computer."""
        query = kwargs.get("query", "")
        
        if not query:
            return {"error": "No search query"}
        
        # Common search locations
        search_paths = [
            Path.home() / "Desktop",
            Path.home() / "Documents",
            Path.home() / "Downloads",
            Path.home() / "Pictures",
            Path.home() / "Videos",
            Path.home() / "Music",
        ]
        
        found_files = []
        query_lower = query.lower()
        
        for search_path in search_paths:
            if search_path.exists():
                try:
                    for item in search_path.rglob("*"):
                        if query_lower in item.name.lower():
                            found_files.append(str(item))
                            if len(found_files) >= 10:  # Limit results
                                break
                except Exception as e:
                    logger.warning(f"Error searching {search_path}: {e}")
        
        return {"found": len(found_files), "files": found_files}
    
    def _open_file(self, **kwargs):
        """Open file or folder."""
        path = kwargs.get("path")
        
        if not path:
            return {"error": "No path specified"}
        
        try:
            os.startfile(path)
            return {"opened": path}
        except Exception as e:
            return {"error": str(e)}
    
    def _navigate_to(self, **kwargs):
        """Navigate to location (folder, website, etc)."""
        location = kwargs.get("location", "")
        
        if not location:
            return {"error": "No location specified"}
        
        # Check if it's a URL
        if location.startswith("http"):
            import webbrowser
            webbrowser.open(location)
            return {"navigated": "web", "url": location}
        
        # Check if it's a file path
        if os.path.exists(location):
            os.startfile(location)
            return {"navigated": "file", "path": location}
        
        # Try common locations
        common_locations = {
            "desktop": Path.home() / "Desktop",
            "documents": Path.home() / "Documents",
            "downloads": Path.home() / "Downloads",
            "pictures": Path.home() / "Pictures",
            "videos": Path.home() / "Videos",
            "music": Path.home() / "Music",
        }
        
        location_lower = location.lower()
        if location_lower in common_locations:
            path = common_locations[location_lower]
            os.startfile(str(path))
            return {"navigated": "folder", "path": str(path)}
        
        return {"error": f"Location not found: {location}"}
    
    def _switch_window(self, **kwargs):
        """Switch between windows."""
        pyautogui.hotkey('alt', 'tab')
        time.sleep(0.3)
        return {"switched": True}
    
    def _close_window(self, **kwargs):
        """Close current window."""
        pyautogui.hotkey('alt', 'f4')
        return {"closed": True}
    
    def _minimize(self, **kwargs):
        """Minimize current window."""
        pyautogui.hotkey('win', 'down')
        return {"minimized": True}
    
    def _maximize(self, **kwargs):
        """Maximize current window."""
        pyautogui.hotkey('win', 'up')
        return {"maximized": True}
    
    def _screenshot(self, **kwargs):
        """Take screenshot."""
        filename = kwargs.get("filename", f"screenshot_{int(time.time())}.png")
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return {"screenshot": filename}
    
    def _find_on_screen(self, **kwargs):
        """Find image or text on screen."""
        query = kwargs.get("query")
        
        if not query:
            return {"error": "No query specified"}
        
        # This would need image recognition - placeholder for now
        return {"found": False, "message": "Image recognition not implemented yet"}
