"""
Conversational JARVIS - Natural dialogue AI assistant

Talk to JARVIS like a real person:
- Natural conversations with context
- Remembers what you talked about
- Can open songs, apps, files
- Controls your laptop
- Friendly personality
"""

import os
import subprocess
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

from jarvis.skills.computer_diagnostics import ComputerDiagnosticsSkill
from jarvis.skills.system_optimizer import SystemOptimizerSkill
from jarvis.skills.music_player import MusicPlayerSkill
from jarvis.skills.get_weather import GetWeatherSkill
from jarvis.skills.web_search import WebSearchSkill
from jarvis.memory.memory_system import MemorySystem


class ConversationalJARVIS:
    """Natural conversational AI assistant."""
    
    def __init__(self, voice_enabled=True):
        """Initialize conversational JARVIS."""
        # Speech
        self.voice_enabled = voice_enabled
        self.recognizer = sr.Recognizer() if voice_enabled else None
        self.microphone = None
        
        if voice_enabled:
            try:
                self.microphone = sr.Microphone()
            except Exception as e:
                print(f"⚠️  Warning: Microphone not available: {e}")
                print("   Running in text-only mode")
                self.voice_enabled = False
        
        # Text-to-speech
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 175)
            self.engine.setProperty('volume', 0.9)
            
            # Set voice
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if "david" in voice.name.lower() or "mark" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"⚠️  Warning: TTS not available: {e}")
            self.engine = None
        
        # LLM for natural conversation
        try:
            from groq import Groq
            self.client = Groq(api_key=os.getenv("LLM_API_KEY"))
            self.llm_provider = "groq"
        except Exception as e:
            print(f"⚠️  Warning: LLM not available: {e}")
            self.client = None
            self.llm_provider = None
        
        # Memory system
        try:
            self.memory = MemorySystem()
        except:
            self.memory = None
        
        # Conversation history
        self.conversation_history = []
        
        # Skills
        self.diagnostics = ComputerDiagnosticsSkill()
        self.optimizer = SystemOptimizerSkill()
        self.music = MusicPlayerSkill()
        self.weather = GetWeatherSkill()
        self.search = WebSearchSkill()
        
        # User info
        self.user_name = os.getenv("USER_NAME", "Sir")
        
        # State
        self.listening = True
        self.last_topic = None
        
        print("🤖 Conversational JARVIS initialized")
        print("   Ready for natural conversation")
        print()
    
    def speak(self, text: str):
        """Speak text naturally."""
        print(f"🗣️  JARVIS: {text}")
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except:
                pass  # Text output is enough if TTS fails
    
    def listen(self) -> str:
        """Listen for speech."""
        if not self.voice_enabled or not self.microphone:
            return ""
            
        with self.microphone as source:
            print("🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                print("🔄 Processing...")
                
                text = self.recognizer.recognize_google(audio)
                print(f"👤 You: {text}")
                return text.lower()
                
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                self.speak("Sorry, my speech recognition is having issues.")
                return ""
    
    def open_application(self, app_name: str) -> bool:
        """Open an application."""
        apps = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "browser": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "firefox": "firefox",
            "edge": "msedge",
            "notepad": "notepad",
            "calculator": "calc",
            "paint": "mspaint",
            "word": "winword",
            "excel": "excel",
            "powerpoint": "powerpnt",
            "spotify": r"C:\Users\{}\AppData\Roaming\Spotify\Spotify.exe".format(os.getenv("USERNAME", "john")),
            "vlc": r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            "code": "code",
            "vscode": "code",
            "visual studio code": "code"
        }
        
        app_cmd = apps.get(app_name.lower())
        if app_cmd:
            try:
                # Check if file exists for full paths
                if app_cmd.startswith("C:") and not os.path.exists(app_cmd):
                    # Try common alternative locations
                    if "chrome" in app_cmd.lower():
                        alt_paths = [
                            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                            r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                        ]
                        for path in alt_paths:
                            if os.path.exists(path):
                                app_cmd = path
                                break
                
                subprocess.Popen(app_cmd, shell=True)
                return True
            except Exception as e:
                print(f"⚠️  Error opening {app_name}: {e}")
                return False
        return False
    
    def play_music(self, query: str = None) -> str:
        """Play music."""
        if query:
            # Try to play specific song
            result = self.music.execute(action="play", query=query)
            if result.success:
                return f"Playing {query}"
            else:
                # Open Spotify or default music player
                if self.open_application("spotify"):
                    return "Opening Spotify for you"
                else:
                    return "I couldn't find a music player. Try installing Spotify."
        else:
            # Just open music player
            if self.open_application("spotify"):
                return "Opening Spotify"
            else:
                return "I couldn't find a music player"
    
    def open_file_or_folder(self, path: str) -> bool:
        """Open a file or folder."""
        try:
            os.startfile(path)
            return True
        except:
            return False
    
    def search_and_open(self, query: str) -> str:
        """Search for and open files/folders."""
        # Common locations
        locations = [
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\Music"),
            os.path.expanduser("~\\Videos"),
            os.path.expanduser("~\\Pictures")
        ]
        
        query_lower = query.lower()
        
        for location in locations:
            if os.path.exists(location):
                for item in os.listdir(location):
                    if query_lower in item.lower():
                        full_path = os.path.join(location, item)
                        if self.open_file_or_folder(full_path):
                            return f"Opening {item}"
        
        return f"I couldn't find {query}"
    
    def get_llm_response(self, user_message: str) -> str:
        """Get natural response from LLM."""
        if not self.client:
            return "I'm having trouble thinking right now."
        
        # Build conversation context
        messages = []
        
        # Add recent history
        for msg in self.conversation_history[-6:]:  # Last 3 exchanges
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # System prompt for JARVIS personality
        system_prompt = f"""You are JARVIS, a friendly and helpful AI assistant like from Iron Man. You're talking to {self.user_name}.

Personality:
- Friendly, warm, and conversational
- Professional but not stiff
- Witty and occasionally humorous
- Proactive and helpful
- Remember context from the conversation

Capabilities you can mention:
- Diagnose and optimize the computer
- Play music and open applications
- Search the web and get weather
- Open files and folders
- Control the laptop
- Have natural conversations

Keep responses concise (1-3 sentences usually). Be natural and conversational.

Current time: {datetime.now().strftime('%I:%M %p')}
Current date: {datetime.now().strftime('%A, %B %d, %Y')}
"""
        
        try:
            if self.llm_provider == "groq":
                response = self.client.chat.completions.create(
                    model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *messages
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                assistant_message = response.choices[0].message.content
            else:
                # Fallback for other providers
                return "I'm having trouble thinking right now."
            
            # Save to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return assistant_message
            
        except Exception as e:
            print(f"⚠️  LLM Error: {e}")
            return "I'm having trouble thinking right now. Could you try again?"
    
    def handle_conversation(self, user_input: str):
        """Handle natural conversation with actions."""
        
        # Check for specific actions first
        
        # Music/Songs
        if any(word in user_input for word in ["play", "music", "song", "spotify"]):
            if "play" in user_input:
                # Extract song name
                words = user_input.split()
                if "play" in words:
                    play_idx = words.index("play")
                    if play_idx + 1 < len(words):
                        song_query = " ".join(words[play_idx + 1:])
                        result = self.play_music(song_query)
                        self.speak(result)
                        return
            
            result = self.play_music()
            self.speak(result)
            return
        
        # Open applications
        if "open" in user_input:
            words = user_input.split()
            if "open" in words:
                open_idx = words.index("open")
                if open_idx + 1 < len(words):
                    app_name = words[open_idx + 1]
                    if self.open_application(app_name):
                        self.speak(f"Opening {app_name}")
                        return
                    else:
                        # Try to find and open file/folder
                        result = self.search_and_open(app_name)
                        self.speak(result)
                        return
        
        # System diagnostics
        if any(word in user_input for word in ["diagnose", "check computer", "system health", "how is my computer"]):
            self.speak("Let me check your computer health.")
            result = self.diagnostics.execute(scan_type="quick")
            
            if result.success:
                data = result.result
                disk_info = data.get("disk", {})
                
                health_score = 100
                for disk in disk_info.get("disks", []):
                    if disk['usage_percent'] > 90:
                        health_score -= 15
                    elif disk['usage_percent'] > 75:
                        health_score -= 5
                
                self.speak(f"Your computer health is {health_score} out of 100.")
                
                if health_score >= 90:
                    self.speak("Everything looks great!")
                elif health_score >= 75:
                    self.speak("Looking good, but could use some cleanup.")
                else:
                    self.speak("Your system needs attention. Want me to clean it up?")
            return
        
        # Clean/optimize
        if any(word in user_input for word in ["clean", "optimize", "free space", "speed up"]):
            self.speak("I'll clean up your system now.")
            result = self.optimizer.execute(action="optimize_all")
            
            if result.success:
                freed = result.result.get("total_freed_gb", 0)
                self.speak(f"Done! I freed up {freed} gigabytes of space.")
            return
        
        # Weather
        if "weather" in user_input:
            self.speak("Let me check the weather for you.")
            result = self.weather.execute(location="current")
            if result.success:
                self.speak(f"The weather is {result.result.get('description', 'nice')}")
            return
        
        # Time
        if "time" in user_input or "what time" in user_input:
            current_time = datetime.now().strftime('%I:%M %p')
            self.speak(f"It's {current_time}")
            return
        
        # Date
        if "date" in user_input or "what day" in user_input or "today" in user_input:
            current_date = datetime.now().strftime('%A, %B %d, %Y')
            self.speak(f"Today is {current_date}")
            return
        
        # Exit
        if any(word in user_input for word in ["goodbye", "bye", "exit", "quit", "stop"]):
            self.speak(f"Goodbye {self.user_name}! I'll be here if you need me.")
            self.listening = False
            return
        
        # Natural conversation - use LLM
        response = self.get_llm_response(user_input)
        self.speak(response)
    
    def run(self):
        """Run conversational JARVIS."""
        # Greeting
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        self.speak(f"{greeting} {self.user_name}! I'm JARVIS, your personal assistant.")
        self.speak("I'm here to help with anything you need. Just talk to me naturally!")
        
        while self.listening:
            user_input = self.listen()
            
            if user_input:
                self.handle_conversation(user_input)


def main():
    """Main entry point."""
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║           Conversational JARVIS Assistant               ║")
    print("║              Talk Naturally - Like a Friend             ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    try:
        jarvis = ConversationalJARVIS()
        jarvis.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  - LLM_API_KEY in .env file")
        print("  - Microphone connected")
        print("  - Internet connection")


if __name__ == "__main__":
    main()
