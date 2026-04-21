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
        from pycaw.pycaw import AudioUtilities
        
        # Get speakers and return the EndpointVolume interface
        speakers = AudioUtilities.GetSpeakers()
        volume = speakers.EndpointVolume
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
    # Method 1: Try pycaw first
    vol = _get_volume_control()
    if vol:
        try:
            vol.SetMute(1 if mute else 0, None)
            logger.info(f"Audio {'muted' if mute else 'unmuted'}")
            return True
        except Exception as e:
            logger.warning(f"pycaw mute failed: {e}")
    
    # Method 2: Use keyboard shortcut (most reliable)
    try:
        import pyautogui
        pyautogui.press('volumemute')
        logger.info(f"Used keyboard mute toggle")
        return True
    except Exception as e:
        logger.warning(f"Keyboard mute failed: {e}")
    
    return False


def _play_on_youtube(query: str):
    """Open YouTube and auto-play first result with enhanced reliability."""
    import webbrowser
    import time
    
    # Build search URL
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    
    # Always open with webbrowser for reliability
    webbrowser.open(search_url)
    logger.info(f"Opening YouTube search for: {query}")
    
    # Wait longer for page to load
    time.sleep(10)  # Increased wait time for slow connections
    
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        
        # Get screen size
        screen_width, screen_height = pyautogui.size()
        logger.info(f"Screen size: {screen_width}x{screen_height}")
        
        # Method 1: Enhanced keyboard navigation (most reliable)
        logger.info("Using enhanced keyboard navigation method")
        try:
            # First, make sure we're focused on the page
            pyautogui.click(screen_width // 2, screen_height // 2)  # Click center of screen
            time.sleep(1)
            
            # Press Tab many times to navigate to first video
            for i in range(25):  # Increased tab count
                pyautogui.press('tab')
                time.sleep(0.08)  # Slightly faster tabbing
            
            # Press Enter to play
            pyautogui.press('enter')
            logger.info("Used keyboard navigation - pressed Enter to play")
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.warning(f"Keyboard navigation failed: {e}")
        
        # Method 2: Try clicking on video thumbnails with more positions
        logger.info("Trying enhanced click method")
        possible_positions = [
            # More positions to try
            (int(screen_width * 0.25), int(screen_height * 0.35)),
            (int(screen_width * 0.20), int(screen_height * 0.30)),
            (int(screen_width * 0.30), int(screen_height * 0.40)),
            (int(screen_width * 0.15), int(screen_height * 0.35)),
            (int(screen_width * 0.35), int(screen_height * 0.35)),
            (400, 300),  # Fixed positions for common resolutions
            (350, 280),
            (450, 320),
            (300, 250),
            (500, 350),
        ]
        
        for pos_x, pos_y in possible_positions:
            try:
                logger.info(f"Trying to click at position: ({pos_x}, {pos_y})")
                pyautogui.moveTo(pos_x, pos_y, duration=0.2)
                time.sleep(0.3)
                pyautogui.click()
                time.sleep(4)  # Wait longer to see if video starts
                
                logger.info(f"Clicked at ({pos_x}, {pos_y})")
                # Don't break here, try all positions for better chance
                
            except Exception as e:
                logger.warning(f"Click at ({pos_x}, {pos_y}) failed: {e}")
                continue
        
        # Method 3: Try using search within page
        logger.info("Trying page search method")
        try:
            # Use Ctrl+F to find video elements
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            pyautogui.write('ago', interval=0.01)  # Search for "ago" in timestamps
            time.sleep(1)
            pyautogui.press('escape')  # Close search
            time.sleep(0.5)
            pyautogui.press('enter')  # Try to activate found element
            logger.info("Used page search method")
            
        except Exception as e:
            logger.warning(f"Page search method failed: {e}")
        
        # Method 4: Fallback - try spacebar to play
        logger.info("Trying spacebar method")
        try:
            time.sleep(2)
            pyautogui.press('space')  # Spacebar often plays/pauses videos
            logger.info("Pressed spacebar to play")
            
        except Exception as e:
            logger.warning(f"Spacebar method failed: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"YouTube auto-play failed: {e}")
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
