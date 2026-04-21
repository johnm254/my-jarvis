# 🚀 START USING JARVIS NOW!

## ⚡ Quick Start (2 Minutes)

### Step 1: Check Your Setup (30 seconds)

```bash
# Make sure you're in the JARVIS directory
cd C:\Users\john\Desktop\jarvis

# Check Python version
python --version
# Should show Python 3.14 or higher

# Check if dependencies are installed
pip list | grep groq
# Should show groq package
```

### Step 2: Verify API Key (30 seconds)

```bash
# Check if .env file exists
cat .env | grep LLM_API_KEY

# Should show:
# LLM_API_KEY=gsk_...
```

✅ If you see your API key, you're ready!

### Step 3: Start JARVIS! (1 minute)

**Option 1: Quick Test (Recommended First Time)**
```bash
python demo_quick_test.py
```

**Option 2: Start Conversational JARVIS**
```bash
python conversational_jarvis.py
```

**Option 3: Use Startup Menu**
```bash
python start_jarvis.py
```

---

## 💬 Try These Commands

Once JARVIS starts, try:

### Greetings
```
"Hello JARVIS"
"Good morning"
"Hey, how are you?"
```

### Music
```
"Play Despacito"
"Play some music"
"Play Ed Sheeran"
```

### Apps
```
"Open Chrome"
"Open Calculator"
"Open Notepad"
```

### System
```
"Check my computer"
"What time is it?"
"What's the date?"
```

### Conversation
```
"What can you do?"
"Tell me a joke"
"Thanks, goodbye"
```

---

## 🎯 What to Expect

### First Run
```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           Conversational JARVIS Assistant               ║
║              Talk Naturally - Like a Friend             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

🤖 Conversational JARVIS initialized
   Ready for natural conversation

🗣️  JARVIS: Good afternoon Sir! I'm JARVIS, your personal assistant.
🗣️  JARVIS: I'm here to help with anything you need. Just talk to me naturally!

🎤 Listening...
```

### Example Interaction
```
👤 You: Hello JARVIS
🗣️  JARVIS: Good afternoon, Sir. How can I help you today?

👤 You: Play some music
🗣️  JARVIS: What would you like to hear?

👤 You: Play Despacito
🗣️  JARVIS: Playing Despacito on YouTube
[YouTube opens and plays the song]

👤 You: Thanks
🗣️  JARVIS: You're welcome! Anything else?
```

---

## 🔧 Troubleshooting

### "LLM_API_KEY not set"
```bash
# Edit .env file
notepad .env

# Add your Groq API key:
LLM_API_KEY=your_key_here

# Get free key from: https://console.groq.com
```

### "Module not found"
```bash
# Install dependencies
pip install -r requirements.txt
```

### "Microphone not found"
```bash
# Use text mode instead (works great!)
python test_conversational_jarvis.py
```

### "Chrome not found"
```bash
# Try other apps first:
"Open Calculator"
"Open Notepad"

# Or edit conversational_jarvis.py to fix Chrome path
```

---

## 📱 Daily Usage

### Morning Routine
```bash
python conversational_jarvis.py
```

Then say:
```
"Good morning JARVIS"
"What's the weather?"
"Play morning music"
"Open Chrome"
```

### Work Session
```
"Open VS Code"
"Play focus music"
"Check my computer"
```

### Evening
```
"Play relaxing music"
"Clean up my system"
"Thanks, goodbye"
```

---

## 🎨 Customize JARVIS

### Change Name
Edit `conversational_jarvis.py`:
```python
self.user_name = os.getenv("USER_NAME", "Your Name")
```

### Add More Apps
Edit `open_application()` method:
```python
apps = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "myapp": r"C:\Path\To\Your\App.exe",  # Add your app
}
```

### Change Personality
Edit the system prompt in `get_llm_response()`:
```python
system_prompt = """You are JARVIS, a [your personality here]..."""
```

---

## 📚 Learn More

- **[User Guide](CONVERSATIONAL_JARVIS_GUIDE.md)** - Complete guide
- **[Quick Start](QUICK_START_CONVERSATIONAL_JARVIS.md)** - Detailed setup
- **[System Overview](COMPLETE_SYSTEM_OVERVIEW.md)** - Architecture

---

## 🎉 You're Ready!

### Right Now:
```bash
python demo_quick_test.py
```

### Then Daily:
```bash
python conversational_jarvis.py
```

### Or Use Menu:
```bash
python start_jarvis.py
```

---

## 💡 Pro Tips

1. **Be Natural** - Talk like chatting with a friend
2. **Ask Follow-ups** - JARVIS remembers context
3. **Be Specific** - "Play Despacito" vs "Play music"
4. **Give Feedback** - "That's perfect, thanks!"
5. **Explore** - Try different commands

---

## 🚀 Advanced Features

### Email-to-Code
Send email to: `johnmwangi1729+jarvis@gmail.com`
```
Subject: [JARVIS] Build My Project
Body: Project requirements...
```

JARVIS will automatically build it!

### System Automation
```
"Check my computer"
"Clean up my system"
"Free up space"
```

### Development Tools
```bash
# List all skills
python jarvis_cli.py skill list

# Run diagnostics
python diagnose_computer.py
```

---

## 🎊 Start Now!

**Everything is ready. Just run:**

```bash
python demo_quick_test.py
```

**Then start using it daily:**

```bash
python conversational_jarvis.py
```

---

**Talk to JARVIS like a friend!** 🤖💬

Your personal AI assistant is ready to help!

---

## 📞 Need Help?

- Check documentation in `docs/` folder
- Read `CONVERSATIONAL_JARVIS_GUIDE.md`
- Review `QUICK_START_CONVERSATIONAL_JARVIS.md`

**Everything is set up and working!** ✅
