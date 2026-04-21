# 🤖 JARVIS - Your Personal AI Assistant

> Talk to JARVIS like a friend. Control your computer, play music, manage tasks, and automate projects - all through natural conversation.

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/Status-Active-success.svg)]()

---

## ✨ Features

### 🗣️ Natural Conversations
Talk to JARVIS like chatting with a friend. No commands needed - just natural language.

```
You: "Hello JARVIS"
JARVIS: "Good afternoon! How can I help you today?"

You: "Play some music"
JARVIS: "What would you like to hear?"

You: "Something upbeat"
JARVIS: "Playing upbeat music on YouTube"
```

### 🎵 Music & Entertainment
- Play any song on YouTube with auto-play
- Search by song, artist, or genre
- Volume control
- Background playback

### 💻 Computer Control
- Open applications (Chrome, VS Code, Spotify, etc.)
- Find and open files/folders
- System diagnostics and optimization
- Disk space management

### 🚀 Development Automation
- Email-to-code pipeline
- Automatic project generation
- GitHub integration
- IDE control

### 🧠 Smart & Contextual
- Remembers your conversation
- Understands follow-up questions
- Proactive suggestions
- Friendly personality

---

## 🚀 Quick Start

### 1. Install

```bash
# Clone the repository
git clone https://github.com/yourusername/jarvis-ai-assistant.git
cd jarvis-ai-assistant

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 2. Configure

Edit `.env` and add your API keys:

```bash
# Required: Get free API key from https://console.groq.com
LLM_API_KEY=your_groq_api_key_here

# Optional: For weather
WEATHER_API_KEY=your_weather_api_key

# Optional: For GitHub automation
GITHUB_TOKEN=your_github_token
```

### 3. Run

```bash
# Quick test (30 seconds)
python demo_quick_test.py

# Start using JARVIS
python conversational_jarvis.py
```

That's it! Start talking to JARVIS naturally.

---

## 💬 Example Usage

### Morning Routine
```
You: "Good morning JARVIS"
JARVIS: "Good morning! How can I help you today?"

You: "What's the weather?"
JARVIS: "It's sunny and 72 degrees. Perfect day!"

You: "Play some morning music"
JARVIS: "Playing upbeat morning playlist"

You: "Open Chrome"
JARVIS: "Opening Chrome"
```

### Work Session
```
You: "I need to work"
JARVIS: "Sure! What would you like me to do?"

You: "Open VS Code"
JARVIS: "Opening VS Code"

You: "Play focus music"
JARVIS: "Playing lo-fi study music"
```

### System Maintenance
```
You: "Check my computer"
JARVIS: "Your system health is 95/100. Disk is 89% full."

You: "Clean it up"
JARVIS: "Cleaning now... Done! Freed 15GB"
```

---

## 🎯 What Can JARVIS Do?

### 🎵 Music & Entertainment
- `"Play Despacito"`
- `"Play Ed Sheeran"`
- `"Play relaxing music"`
- `"Volume up"`

### 💻 Application Control
- `"Open Chrome"`
- `"Open VS Code"`
- `"Open Calculator"`
- `"Open my documents"`

### 🔧 System Operations
- `"Check my computer"`
- `"Clean up my system"`
- `"Free up space"`
- `"How much disk space?"`

### ℹ️ Information
- `"What time is it?"`
- `"What's the date?"`
- `"What's the weather?"`

### 🚀 Development (Advanced)
- Email project requirements → JARVIS builds it
- Automatic code generation
- GitHub repository creation
- IDE integration

---

## 📚 Documentation

- **[Quick Start Guide](QUICK_START_CONVERSATIONAL_JARVIS.md)** - Get started in 5 minutes
- **[User Guide](CONVERSATIONAL_JARVIS_GUIDE.md)** - Complete usage guide
- **[System Overview](COMPLETE_SYSTEM_OVERVIEW.md)** - Architecture details
- **[Skills Documentation](docs/skills_architecture.md)** - Available skills

---

## 🔧 Requirements

- **Python 3.14+** (or 3.10+)
- **Internet connection** (for LLM and music)
- **Microphone** (optional, for voice mode)
- **Windows/Linux/Mac** (tested on Windows)

### Dependencies
```
groq              # LLM integration
speech_recognition # Voice input (optional)
pyttsx3           # Text-to-speech (optional)
pyautogui         # YouTube auto-play
python-dotenv     # Configuration
```

All dependencies install automatically with `pip install -r requirements.txt`

---

## 🎤 Voice Mode (Optional)

JARVIS works great in text mode, but you can enable voice:

### Windows
```bash
# Install C++ Build Tools first
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

pip install pyaudio
python conversational_jarvis.py
```

### Linux
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
python conversational_jarvis.py
```

### Mac
```bash
brew install portaudio
pip install pyaudio
python conversational_jarvis.py
```

---

## 🏗️ Architecture

### Core Components
- **Conversational Interface** - Natural language understanding
- **LLM Integration** - Groq/Llama 3.3 70B for intelligence
- **Skills System** - 25+ modular capabilities
- **Memory System** - Context and conversation history
- **Voice Control** - Speech recognition and TTS

### Skills (25 Total)
- **Communication** (4): Email, meetings, notifications
- **Development** (6): Project automation, code generation
- **System** (5): Diagnostics, optimization, file management
- **Productivity** (5): Tasks, notes, reminders, calendar
- **Research** (2): Web search, weather
- **Personal** (3): Music, smart home, fitness

---

## 🎨 Customization

### Add Custom Skills
```python
# jarvis/skills/my_skill.py
from jarvis.skills.base import Skill, SkillResult

class MySkill(Skill):
    def __init__(self):
        super().__init__()
        self._name = "my_skill"
        self._description = "What my skill does"
    
    def execute(self, **kwargs) -> SkillResult:
        # Your code here
        return SkillResult(success=True, result="Done!")
```

### Customize Personality
Edit `conversational_jarvis.py` to change JARVIS's personality, responses, and behavior.

### Add Applications
Edit the `open_application()` method to add more apps JARVIS can open.

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by Iron Man's JARVIS
- Built with [Groq](https://groq.com) for fast LLM inference
- Uses [OpenJarvis](https://openjarvis.com) architecture principles
- Follows [agentskills.io](https://agentskills.io) standards

---

## 🐛 Troubleshooting

### "LLM_API_KEY not set"
Get a free API key from [Groq Console](https://console.groq.com) and add it to `.env`

### "PyAudio not found"
Voice mode is optional. Use text mode or install PyAudio (see Voice Mode section)

### "Chrome not found"
Edit `conversational_jarvis.py` and update the Chrome path for your system

### More Issues?
Check the [documentation](CONVERSATIONAL_JARVIS_GUIDE.md) or open an issue

---

## 📊 Status

- ✅ Natural conversations - Working
- ✅ Music control - Working
- ✅ App control - Working
- ✅ System operations - Working
- ✅ Development automation - Working
- ✅ Voice control - Optional
- ✅ 25 skills - All operational

---

## 🎉 Start Now!

```bash
# Quick test
python demo_quick_test.py

# Start using JARVIS
python conversational_jarvis.py
```

**Talk to JARVIS like a friend!** 🤖💬

---

## 📞 Support

- **Documentation**: See `docs/` folder
- **Issues**: Open a GitHub issue
- **Discussions**: GitHub Discussions
- **Email**: your-email@example.com

---

**Made with ❤️ by developers, for developers**

⭐ Star this repo if you find it helpful!
