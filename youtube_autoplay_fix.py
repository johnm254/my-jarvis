"""
Enhanced YouTube auto-play with multiple fallback methods
"""

import time
import webbrowser
import pyautogui

def enhanced_youtube_play(query: str):
    """Enhanced YouTube auto-play with multiple methods."""
    
    print(f"🎵 Playing: {query}")
    
    # Build search URL
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    
    # Open YouTube
    webbrowser.open(search_url)
    print("   📂 Opened YouTube")
    
    # Wait for page to load
    print("   ⏳ Waiting for page to load...")
    time.sleep(8)
    
    pyautogui.FAILSAFE = False
    screen_width, screen_height = pyautogui.size()
    print(f"   📺 Screen size: {screen_width}x{screen_height}")
    
    # Method 1: Click on video thumbnail
    print("   🖱️  Method 1: Trying to click video thumbnail...")
    positions = [
        (int(screen_width * 0.25), int(screen_height * 0.35)),
        (int(screen_width * 0.20), int(screen_height * 0.30)),
        (400, 300),
        (350, 280),
    ]
    
    for i, (x, y) in enumerate(positions):
        try:
            print(f"      Clicking position {i+1}: ({x}, {y})")
            pyautogui.moveTo(x, y, duration=0.3)
            pyautogui.click()
            time.sleep(3)
            print(f"      ✅ Clicked at ({x}, {y})")
            return True
        except Exception as e:
            print(f"      ❌ Click failed: {e}")
    
    # Method 2: Keyboard navigation
    print("   ⌨️  Method 2: Trying keyboard navigation...")
    try:
        for i in range(20):
            pyautogui.press('tab')
            time.sleep(0.1)
        pyautogui.press('enter')
        print("      ✅ Used keyboard navigation (Tab + Enter)")
        return True
    except Exception as e:
        print(f"      ❌ Keyboard navigation failed: {e}")
    
    # Method 3: Search and click
    print("   🔍 Method 3: Trying search and click...")
    try:
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)
        pyautogui.write('ago')
        time.sleep(0.5)
        pyautogui.press('escape')
        pyautogui.press('enter')
        print("      ✅ Used search and click method")
        return True
    except Exception as e:
        print(f"      ❌ Search and click failed: {e}")
    
    # Method 4: Direct URL approach
    print("   🎯 Method 4: Trying direct video URL...")
    try:
        # Try to get the first video URL and navigate directly
        direct_url = f"https://www.youtube.com/watch?v={query.replace(' ', '+')}"
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)
        pyautogui.write(direct_url)
        pyautogui.press('enter')
        print("      ✅ Tried direct video URL")
        return True
    except Exception as e:
        print(f"      ❌ Direct URL failed: {e}")
    
    print("   ❌ All methods failed")
    return False

if __name__ == "__main__":
    # Test the enhanced auto-play
    enhanced_youtube_play("Despacito")
    
    print("\n🔍 Check your browser:")
    print("   - Did YouTube open?")
    print("   - Did a video start playing?")
    print("   - If not, which method got closest?")