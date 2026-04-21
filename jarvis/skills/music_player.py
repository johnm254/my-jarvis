"""Music Player Skill — auto-play music + volume control."""

import os
import time
import logging
import threading
import webbrowser
import subprocess
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


def _get_volume_control():
    """Get Windows volume control interface."""
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        return volume
    except Exception as e:
        logger.warning(f"Could not get volume control: {e}")
        return None


def _set_volume(level: float) -> bool:
    """Set system volume 0.0–1.0."""
    vol = _get_volume_control()
    if vol:
        try:
            vol.SetMasterVolumeLevelScalar(max(0.0, min(1.0, level)), None)
            logger.info(f"Volume set to {int(level * 100)}%")
            return True
        except Exception as e:
            logger.warning(f"Failed to set volume: {e}")
    
    # Fallback: Use nircmd if available
    try:
        pct = int(level * 65535)  # nircmd uses 0-65535 range
        subprocess.run(["nircmd.exe", "setsysvolume", str(pct)], 
                      capture_output=True, timeout=2)
        return True
    except Exception:
        pass
    
    return False


def _get_volume() -> int:
    """Get current system volume (0-100)."""
    vol = _get_volume_control()
    if vol:
        try:
            current = vol.GetMasterVolumeLevelScalar()
            return int(current * 100)
        except Exception as e:
            logger.warning(f"Failed to get volume: {e}")
    return 50  # Default fallback


def _change_volume(delta: float) -> int:
    """Change volume by delta (-1.0 to +1.0)."""
    current = _get_volume() / 100.0
    new = max(0.0, min(1.0, current + delta))
    _set_volume(new)
    return int(new * 100)


def _mute_toggle(mute: bool) -> bool:
    """Mute or unmute system audio."""
    vol = _get_volume_control()
    if vol:
        try:
            vol.SetMute(1 if mute else 0, None)
            logger.info(f"Audio {'muted' if mute else 'unmuted'}")
            return True
        except Exception as e:
            logger.warning(f"Failed to toggle mute: {e}")
    
    # Fallback: Use nircmd
    try:
        cmd = "mutesysvolume 1" if mute else "mutesysvolume 0"
        subprocess.run(["nircmd.exe"] + cmd.split(), 
                      capture_output=True, timeout=2)
        return True
    except Exception:
        pass
    
    return False


def _play_on_youtube(query: str):
    """Open YouTube and auto-play first result using pyautogui."""
    import webbrowser
    import time
    
    # Open YouTube search
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(search_url)
    
    # Wait for page to load
    time.sleep(5)
    
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        
        # Method 1: Click on first video thumbnail
        # Move to approximate position of first video (adjust if needed)
        screen_width, screen_height = pyautogui.size()
        
        # First video is usually around 20% from left, 30% from top
        first_video_x = int(screen_width * 0.20)
        first_video_y = int(screen_height * 0.30)
        
        # Move mouse to first video position
        pyautogui.moveTo(first_video_x, first_video_y, duration=0.5)
        time.sleep(0.3)
        
        # Click to play
        pyautogui.click()
        time.sleep(1)
        
        # Press 'f' for fullscreen (optional)
        # pyautogui.press('f')
        
        logger.info(f"Auto-played YouTube video for: {query}")
        return True
        
    except Exception as e:
        logger.warning(f"pyautogui auto-play failed: {e}")
        
        # Fallback: Try keyboard navigation
        try:
            import pyautogui
            time.sleep(2)
            # Tab to first video and press Enter
            for _ in range(8):
                pyautogui.press('tab')
                time.sleep(0.2)
            pyautogui.press('enter')
            logger.info(f"Auto-played via keyboard for: {query}")
            return True
        except Exception as e2:
            logger.warning(f"Keyboard fallback failed: {e2}")
            return False


class MusicPlayerSkill(Skill):
    """Play music on YouTube (auto-plays) and control system volume."""

    def __init__(self):
        super().__init__()
        self._name = "music_player"
        self._description = (
            "Play any song or music on YouTube — searches and auto-plays. "
            "Also controls system volume: increase, decrease, set level, mute, unmute."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": (
                        "What to do: 'play' to play a song, "
                        "'volume_up' to increase volume, "
                        "'volume_down' to decrease volume, "
                        "'set_volume' to set exact level, "
                        "'mute' to mute, 'unmute' to unmute, "
                        "'get_volume' to check current volume"
                    ),
                },
                "query": {
                    "type": "string",
                    "description": "Song name, artist, or genre to play.",
                },
                "level": {
                    "type": "number",
                    "description": "Volume level 0-100 for set_volume action.",
                },
            },
            "required": ["action"],
        }

    def execute(self, **kwargs) -> SkillResult:
        start = time.time()
        action = kwargs.get("action", "play")
        query = kwargs.get("query", "")
        level = kwargs.get("level")

        try:
            if action == "play":
                if not query:
                    return SkillResult(success=False, result=None,
                                       error_message="No song specified.",
                                       execution_time_ms=int((time.time()-start)*1000))
                # Run in background thread so JARVIS can keep talking
                threading.Thread(
                    target=_play_on_youtube, args=(query,), daemon=True
                ).start()
                return SkillResult(
                    success=True,
                    result={"playing": query, "method": "youtube_autoplay"},
                    execution_time_ms=int((time.time()-start)*1000),
                )

            elif action == "volume_up":
                new_vol = _change_volume(+0.10)
                return SkillResult(success=True,
                                   result={"volume": new_vol},
                                   execution_time_ms=int((time.time()-start)*1000))

            elif action == "volume_down":
                new_vol = _change_volume(-0.10)
                return SkillResult(success=True,
                                   result={"volume": new_vol},
                                   execution_time_ms=int((time.time()-start)*1000))

            elif action == "set_volume":
                if level is None:
                    return SkillResult(success=False, result=None,
                                       error_message="Specify level 0-100.",
                                       execution_time_ms=int((time.time()-start)*1000))
                _set_volume(float(level) / 100.0)
                return SkillResult(success=True,
                                   result={"volume": int(level)},
                                   execution_time_ms=int((time.time()-start)*1000))

            elif action == "mute":
                _mute_toggle(True)
                return SkillResult(success=True, result="Muted.",
                                   execution_time_ms=int((time.time()-start)*1000))

            elif action == "unmute":
                _mute_toggle(False)
                return SkillResult(success=True, result="Unmuted.",
                                   execution_time_ms=int((time.time()-start)*1000))

            elif action == "get_volume":
                vol = _get_volume()
                return SkillResult(success=True,
                                   result={"volume": vol},
                                   execution_time_ms=int((time.time()-start)*1000))

            else:
                return SkillResult(success=False, result=None,
                                   error_message=f"Unknown action: {action}",
                                   execution_time_ms=int((time.time()-start)*1000))

        except Exception as e:
            return SkillResult(success=False, result=None, error_message=str(e),
                               execution_time_ms=int((time.time()-start)*1000))
