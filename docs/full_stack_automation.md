# Full-Stack Project Automation

JARVIS can now automate the complete software development lifecycle from email to deployment.

## Overview

The full-stack automation workflow consists of 6 integrated skills that work together to deliver complete projects:

```
Email → Requirements → Architecture → Code → GitHub → Deployment → Notification
```

## Skills

### 1. Email Intake (`email_intake`)

Polls Gmail inbox and extracts structured requirements using Claude.

**Actions:**
- `poll` - Check inbox for project emails
- `parse` - Extract requirements from email body

**Extracts:**
- Project name
- Tech stack
- Features list
- Deadline
- Additional notes

**Output:** JSON spec file for downstream consumption

**Example:**
```python
from jarvis.skills.email_intake import EmailIntakeSkill

skill = EmailIntakeSkill()
result = skill.execute(
    action="parse",
    email_body=email_text,
    output_path="specs/project_spec.json"
)
```

---

### 2. Project Architect (`project_architect`)

Generates complete project architecture from requirements spec.

**Generates:**
- Folder structure (framework-specific)
- ERD (Entity Relationship Diagram) in Mermaid format
- API contract (OpenAPI 3.0 specification)
- Component diagram (Mermaid format)
- PLAN.md implementation blueprint

**Supports:**
- React, Next.js, Vue
- Node.js, Express, FastAPI, Django
- TypeScript, Python

**Example:**
```python
from jarvis.skills.project_architect import ProjectArchitectSkill

skill = ProjectArchitectSkill()
result = skill.execute(
    spec_path="specs/project_spec.json",
    output_dir="architecture/my_project"
)
```

**Output Files:**
- `folder_structure.txt` - Directory tree
- `erd.mmd` - Database schema diagram
- `openapi.json` - API specification
- `components.mmd` - Architecture diagram
- `PLAN.md` - Implementation plan

---

### 3. Code Generator (`code_generator`)

Agentic code generation with iterative testing and auto-fixing.

**Actions:**
- `generate` - Create code from plan
- `test` - Run test suite
- `lint` - Check code quality
- `fix` - Auto-fix issues
- `iterate` - Full loop until tests pass

**Features:**
- File-by-file code generation
- Automatic test execution (Jest/Pytest)
- Linting (ESLint/Ruff)
- Auto-fix errors
- Iterative improvement loop

**Example:**
```python
from jarvis.skills.code_generator import CodeGeneratorSkill

skill = CodeGeneratorSkill()
result = skill.execute(
    action="iterate",
    plan_path="architecture/PLAN.md",
    output_dir="generated_code/my_project",
    max_iterations=5
)
```

**Workflow:**
1. Generate initial code scaffold
2. Run tests
3. Run linter
4. Auto-fix errors
5. Repeat until tests pass or max iterations reached

---

### 4. GitHub Automation (`github_automation`)

Automates GitHub repository operations.

**Actions:**
- `create_repo` - Create new GitHub repository
- `push` - Push code with meaningful commits
- `create_branch` - Create and push branch
- `open_pr` - Open pull request
- `clone` - Clone repository
- `fetch` - Fetch latest changes

**Requirements:**
- GitHub CLI (`gh`) installed
- `GITHUB_TOKEN` environment variable

**Example:**
```python
from jarvis.skills.github_automation import GitHubAutomationSkill

skill = GitHubAutomationSkill()

# Create repo
skill.execute(
    action="create_repo",
    repo_name="my-awesome-project",
    private=False
)

# Push code
skill.execute(
    action="push",
    local_path="./my_project",
    commit_message="feat: initial implementation"
)

# Create dev branch
skill.execute(
    action="create_branch",
    local_path="./my_project",
    branch_name="dev"
)

# Open PR
skill.execute(
    action="open_pr",
    local_path="./my_project",
    pr_title="feat: Initial Implementation",
    pr_body="Automated PR with full feature set"
)
```

---

### 5. IDE Control (`ide_control`)

Controls local development environment.

**Actions:**
- `open_vscode` - Open project in VS Code
- `install_deps` - Install dependencies (npm/pip/yarn/pnpm)
- `start_server` - Start dev server in background
- `tail_log` - Read log files
- `run_command` - Execute custom shell commands

**Example:**
```python
from jarvis.skills.ide_control import IDEControlSkill

skill = IDEControlSkill()

# Open in VS Code
skill.execute(
    action="open_vscode",
    project_path="./my_project"
)

# Install dependencies
skill.execute(
    action="install_deps",
    project_path="./my_project",
    package_manager="npm"
)

# Start dev server
skill.execute(
    action="start_server",
    project_path="./my_project",
    server_command="npm run dev"
)
```

---

### 6. Project Completion (`project_completion`)

Sends completion notification email with project summary.

**Includes:**
- Repository link
- Pull request link
- Features implemented
- Test results
- Warnings/issues

**Example:**
```python
from jarvis.skills.project_completion import ProjectCompletionSkill

skill = ProjectCompletionSkill()
result = skill.execute(
    recipient="client@example.com",
    project_name="TaskMaster Pro",
    repo_url="https://github.com/user/taskmaster-pro",
    pr_url="https://github.com/user/taskmaster-pro/pull/1",
    features=[
        "User authentication",
        "Task management",
        "Dashboard with analytics"
    ],
    warnings=[
        "Manual review recommended for auth flow"
    ],
    test_results={
        "passed": 15,
        "failed": 0,
        "coverage": "87%"
    }
)
```

---

## Complete Workflow Example

See `demo_full_stack_automation.py` for a complete end-to-end example.

```bash
python demo_full_stack_automation.py
```

This demonstrates:
1. Parsing project requirements from email
2. Generating architecture and design docs
3. Generating code with iterative testing
4. Creating GitHub repo and opening PR
5. Opening project in VS Code
6. Sending completion notification

---

## Environment Setup

### Required Environment Variables

```bash
# LLM for requirement extraction and code generation
LLM_API_KEY=your_llm_api_key

# GitHub automation
GITHUB_TOKEN=your_github_token

# Email (optional, for full integration)
GMAIL_CREDENTIALS=path/to/credentials.json
```

### Required Tools

1. **GitHub CLI** - For repository operations
   ```bash
   # Windows (using winget)
   winget install GitHub.cli
   
   # Or download from https://cli.github.com/
   ```

2. **Git** - For version control
   ```bash
   git --version
   ```

3. **VS Code** - For IDE integration
   ```bash
   code --version
   ```

4. **Node.js** (for JavaScript projects)
   ```bash
   node --version
   npm --version
   ```

5. **Python** (for Python projects)
   ```bash
   python --version
   pip --version
   ```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    JARVIS Core Orchestrator                 │
│                  (routes tasks to skill layers)             │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Skill 1      │    │  Skill 2      │    │  Skill 3      │
│  Email Intake │───▶│  Architect    │───▶│  Code Gen     │
│               │    │               │    │               │
│ • Poll Gmail  │    │ • Folder      │    │ • Generate    │
│ • Parse reqs  │    │ • ERD         │    │ • Test        │
│ • Extract     │    │ • API spec    │    │ • Lint        │
│   tasks       │    │ • Diagrams    │    │ • Fix         │
└───────────────┘    └───────────────┘    └───────────────┘
                                                   │
        ┌──────────────────────────────────────────┘
        │
        ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Skill 4      │    │  Skill 5      │    │  Skill 6      │
│  GitHub       │───▶│  IDE Control  │───▶│  Completion   │
│               │    │               │    │               │
│ • Create repo │    │ • Open VS Code│    │ • Send email  │
│ • Push code   │    │ • Install deps│    │ • Summary     │
│ • Create PR   │    │ • Start server│    │ • Links       │
└───────────────┘    └───────────────┘    └───────────────┘
```

---

## Supporting Infrastructure

### Memory & Context Store

Use existing JARVIS memory system (Supabase) to store:
- Project state across sessions
- Generated artifacts
- Build history
- Error logs

### Task Scheduler

Options for automation:
- **Python**: `schedule` library or `APScheduler`
- **Node.js**: `node-cron`
- **System**: Windows Task Scheduler, cron
- **Cloud**: GitHub Actions, AWS EventBridge

### Secrets Management

Store API keys securely:
- `.env` file (development)
- Doppler (recommended)
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault

---

## Customization

### Adding Custom Templates

Edit skill files to add your own templates:

**Code Generator Templates:**
```python
# jarvis/skills/code_generator.py
def _generate_code(self, plan_path: str, output_dir: str):
    # Add your custom templates here
    pass
```

**Architecture Templates:**
```python
# jarvis/skills/project_architect.py
def _generate_folder_structure(self, spec: Dict[str, Any]):
    # Customize folder structures
    pass
```

### Extending Skills

Create new skills by inheriting from `Skill` base class:

```python
from jarvis.skills.base import Skill, SkillResult

class MyCustomSkill(Skill):
    def __init__(self):
        super().__init__()
        self._name = "my_custom_skill"
        self._description = "Does something awesome"
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> SkillResult:
        # Your implementation
        pass
```

---

## Troubleshooting

### GitHub CLI Not Found
```bash
# Install GitHub CLI
winget install GitHub.cli

# Authenticate
gh auth login
```

### VS Code Not Opening
```bash
# Add VS Code to PATH
# Windows: Add C:\Program Files\Microsoft VS Code\bin to PATH
```

### Tests Failing
```bash
# Check test framework installation
npm list jest  # For JavaScript
pip list | grep pytest  # For Python
```

### Git Push Fails
```bash
# Check remote
git remote -v

# Set remote
git remote add origin https://github.com/user/repo.git
```

---

## Future Enhancements

- [ ] Docker containerization support
- [ ] Kubernetes deployment automation
- [ ] CI/CD pipeline generation (GitHub Actions, GitLab CI)
- [ ] Database migration automation
- [ ] API documentation generation (Swagger UI)
- [ ] E2E test generation (Playwright, Cypress)
- [ ] Performance monitoring setup
- [ ] Error tracking integration (Sentry)
- [ ] Cloud deployment (AWS, Azure, GCP)
- [ ] Multi-language support (Go, Rust, Java)

---

## License

Part of the JARVIS Personal AI Assistant project.
