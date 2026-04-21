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
    try:
        from pycaw.pycaw import AudioUtilities
        return AudioUtilities.GetSpeakers().EndpointVolume
    except Exception:
        return None


def _set_volume(level: float) -> bool:
    """Set system volume 0.0–1.0."""
    vol = _get_volume_control()
    if vol:
        vol.SetMasterVolumeLevelScalar(max(0.0, min(1.0, level)), None)
        return True
    # Fallback: nircmd or powershell
    try:
        pct = int(level * 100)
        subprocess.run(
            ["powershell", "-c",
             f"$obj = New-Object -ComObject WScript.Shell; "
             f"for($i=0;$i -lt 50;$i++){{$obj.SendKeys([char]174)}}; "
             f"for($i=0;$i -lt {pct//2};$i++){{$obj.SendKeys([char]175)}}"],
            capture_output=True, timeout=5
        )
        return True
    except Exception:
        return False


def _get_volume() -> int:
    vol = _get_volume_control()
    if vol:
        return int(vol.GetMasterVolumeLevelScalar() * 100)
    return 50


def _change_volume(delta: float) -> int:
    current = _get_volume() / 100.0
    new = max(0.0, min(1.0, current + delta))
    _set_volume(new)
    return int(new * 100)


def _mute_toggle(mute: bool):
    vol = _get_volume_control()
    if vol:
        vol.SetMute(1 if mute else 0, None)
        return True
    # Fallback: mute key
    try:
        subprocess.run(
            ["powershell", "-c",
             "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"],
            capture_output=True, timeout=3
        )
        return True
    except Exception:
        return False


def _play_on_youtube(query: str):
    """Open YouTube search and auto-click first result using pyautogui."""
    import webbrowser, time

    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(search_url)

    # Wait for browser to load then use keyboard to navigate to first video
    time.sleep(4)
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        # Tab to first video link and press Enter
        pyautogui.hotkey('alt', 'tab')  # focus browser
        time.sleep(0.5)
        # Press Tab several times to reach first video, then Enter
        for _ in range(5):
            pyautogui.press('tab')
            time.sleep(0.15)
        pyautogui.press('enter')
        logger.info(f"Auto-clicked first YouTube result for: {query}")
        return True
    except Exception as e:
        logger.warning(f"pyautogui auto-click failed: {e}")
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
