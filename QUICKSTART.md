# JARVIS Quick Start Guide

## 🚀 Project is Running!

JARVIS is now operational with 17 skills and full-stack automation capabilities.

---

## ✅ System Status

```
🏥 Diagnostics: All checks passed
📚 Skills: 17 registered and operational
🔧 Configuration: Loaded from .env
🐍 Python: 3.14.0
💻 OS: Windows 10
```

---

## 🎯 What You Can Do Right Now

### 1. List Available Skills

```bash
python jarvis_cli.py skill list
```

**Output:** 17 skills across 6 categories:
- Communication (3)
- Development (5)
- Productivity (3)
- Research (2)
- System (2)
- Personal (2)

### 2. Run Full-Stack Automation Demo

```bash
python demo_full_stack_automation.py
```

**What it does:**
1. Extracts requirements from email
2. Generates project architecture
3. Generates code with tests
4. Creates GitHub repo (needs `gh` CLI)
5. Opens in VS Code
6. Sends completion notification

**Time:** ~53 seconds

### 3. Search for Skills

```bash
python jarvis_cli.py skill search "email"
python jarvis_cli.py skill search "code"
python jarvis_cli.py skill search "github"
```

### 4. Check System Health

```bash
python -c "from jarvis_cli import cmd_doctor; import argparse; args = argparse.Namespace(); cmd_doctor(args)"
```

---

## 📋 Available Commands

### Initialization
```bash
python jarvis_cli.py init                    # Detect hardware
```

### Skill Management
```bash
python jarvis_cli.py skill list              # List all skills
python jarvis_cli.py skill list --category development
python jarvis_cli.py skill search "query"    # Search skills
python jarvis_cli.py skill install hermes:arxiv
```

### Optimization (Coming Soon)
```bash
python jarvis_cli.py optimize skills --policy dspy
python jarvis_cli.py bench skills --max-samples 5
```

---

## 🛠️ Development Workflow

### Create a New Project from Email

1. **Extract Requirements**
```python
from jarvis.skills.email_intake import EmailIntakeSkill

skill = EmailIntakeSkill()
result = skill.execute(
    action="parse",
    email_body="Your project email here...",
    output_path="specs/my_project.json"
)
```

2. **Generate Architecture**
```python
from jarvis.skills.project_architect import ProjectArchitectSkill

skill = ProjectArchitectSkill()
result = skill.execute(
    spec_path="specs/my_project.json",
    output_dir="architecture/my_project"
)
```

3. **Generate Code**
```python
from jarvis.skills.code_generator import CodeGeneratorSkill

skill = CodeGeneratorSkill()
result = skill.execute(
    action="iterate",
    plan_path="architecture/my_project/PLAN.md",
    output_dir="generated_code/my_project",
    max_iterations=5
)
```

4. **Open in VS Code**
```python
from jarvis.skills.ide_control import IDEControlSkill

skill = IDEControlSkill()
skill.execute(
    action="open_vscode",
    project_path="generated_code/my_project"
)
```

---

## 📁 Generated Files

After running the demo, check these directories:

```
jarvis_output/
├── specs/
│   └── taskmaster_spec.json          # Extracted requirements
├── architecture/
│   └── taskmaster/
│       ├── folder_structure.txt      # Project structure
│       ├── erd.mmd                   # Database schema
│       ├── openapi.json              # API specification
│       ├── components.mmd            # Architecture diagram
│       └── PLAN.md                   # Implementation plan
└── generated_code/
    └── taskmaster/
        ├── index.js                  # Express server
        ├── index.test.js             # Tests
        ├── package.json              # Dependencies
        └── node_modules/             # Installed packages
```

---

## 🔧 Configuration

Your `.env` file is configured with:

✅ LLM API (Groq)  
✅ Memory System (Supabase)  
✅ GitHub Token  
✅ Weather API  
⚠️ Gmail (needs OAuth setup)  
⚠️ Google Calendar (needs OAuth setup)  

---

## 🎨 Skill Categories

### Communication
- **email_intake** - Extract requirements from emails
- **manage_email** - Read, summarize, draft emails
- **project_completion** - Send completion notifications

### Development
- **project_architect** - Generate architecture & design
- **code_generator** - Agentic code generation with testing
- **github_automation** - Repo creation, PRs, branches
- **ide_control** - VS Code, package managers, dev servers
- **dev_tools** - Git, npm, docker, boilerplate

### Productivity
- **manage_calendar** - Google Calendar operations
- **set_reminder** - Reminder management
- **daily_brief** - Morning digest

### Research
- **web_search** - Brave Search API
- **github_summary** - GitHub activity summaries

### System
- **system_status** - Resource monitoring
- **run_code** - Code execution sandbox

### Personal
- **get_weather** - Weather information
- **smart_home** - Home Assistant control

---

## 🚀 Next Steps

### Immediate Actions

1. **Install GitHub CLI** (for full automation)
```bash
winget install GitHub.cli
gh auth login
```

2. **Try Individual Skills**
```python
from jarvis.skills.get_weather import GetWeatherSkill

skill = GetWeatherSkill()
result = skill.execute(location="London")
print(result.result)
```

3. **Explore Generated Code**
```bash
cd jarvis_output/generated_code/taskmaster
code .
npm test
```

### Extend JARVIS

1. **Create Custom Skill**
   - See `docs/skills_architecture.md`
   - Follow agentskills.io standard

2. **Install External Skills**
```bash
python jarvis_cli.py skill install hermes:arxiv
python jarvis_cli.py skill install openclaw:web-search
```

3. **Optimize Skills**
```bash
python jarvis_cli.py optimize skills --policy dspy
```

---

## 📚 Documentation

- **Skills Architecture:** `docs/skills_architecture.md`
- **Full-Stack Automation:** `docs/full_stack_automation.md`
- **API Reference:** `docs/api_reference.md`
- **Project Status:** `PROJECT_STATUS.md`

---

## 🐛 Troubleshooting

### GitHub CLI Not Found
```bash
winget install GitHub.cli
```

### Git Repository Error
```bash
cd jarvis_output/generated_code/taskmaster
git init
```

### Import Errors
```bash
pip install -r requirements.txt
```

### Environment Variables
Check `.env` file has all required keys

---

## 💡 Example Use Cases

### 1. Generate a React App
```bash
# Create email with requirements
# Run: python demo_full_stack_automation.py
# Result: Full React app with tests
```

### 2. Check System Status
```python
from jarvis.skills.system_status import SystemStatusSkill

skill = SystemStatusSkill()
result = skill.execute(action="cpu")
```

### 3. Search the Web
```python
from jarvis.skills.web_search import WebSearchSkill

skill = WebSearchSkill()
result = skill.execute(query="Python best practices")
```

### 4. Get Weather
```python
from jarvis.skills.get_weather import GetWeatherSkill

skill = GetWeatherSkill()
result = skill.execute(location="New York")
```

---

## 🎉 Success!

JARVIS is now running with:
- ✅ 17 operational skills
- ✅ Full-stack automation workflow
- ✅ OpenJarvis-style architecture
- ✅ AgentSkills.io standard compliance
- ✅ Complete documentation

**You're ready to build!** 🚀

---

## 📞 Support

- Check `docs/` for detailed guides
- Review `PROJECT_STATUS.md` for current state
- See `demo_full_stack_automation.py` for examples
- Read `docs/skills_architecture.md` for skill development

---

**Happy Building!** 🎯
