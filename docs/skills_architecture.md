# Skills Architecture

JARVIS follows the OpenJarvis model for modular, discoverable skills that follow the [agentskills.io](https://agentskills.io/specification) open standard.

## Philosophy

**Skills are tools that agents discover and invoke on demand.**

Every skill is:
- **Modular** - Self-contained with clear inputs/outputs
- **Discoverable** - Registered in a central catalog
- **Interoperable** - Follows agentskills.io standard
- **Optimizable** - Can be improved from trace data
- **Benchmarkable** - Performance can be measured

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    JARVIS Brain                         │
│              (Orchestrates skill execution)             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Skill Catalog                         │
│         (Discovery, registration, management)           │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Local      │  │   Hermes     │  │  OpenClaw    │
│   Skills     │  │   Agent      │  │   Skills     │
│              │  │   (~150)     │  │  (~13,700)   │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Skill Standard

All skills follow the agentskills.io specification:

```python
from jarvis.skills.skill_standard import SkillSpec, SkillType, SkillCategory

skill = SkillSpec(
    name="email_intake",
    version="1.0.0",
    description="Extract requirements from project emails",
    type=SkillType.INTEGRATION,
    category=SkillCategory.COMMUNICATION,
    author="JARVIS",
    input_schema={
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["poll", "parse"]},
            "email_body": {"type": "string"}
        },
        "required": ["action"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "project_name": {"type": "string"},
            "stack": {"type": "array"},
            "features": {"type": "array"}
        }
    },
    tags=["email", "requirements", "parsing"],
    cost_estimate="low",
    latency_estimate="fast"
)
```

## Skill Types

Following agentskills.io:

- **TOOL** - External API or system call
- **REASONING** - Prompt-based reasoning pattern
- **WORKFLOW** - Multi-step orchestration
- **MEMORY** - State management
- **INTEGRATION** - Third-party service

## Skill Categories

- **COMMUNICATION** - Email, messaging, notifications
- **PRODUCTIVITY** - Calendar, tasks, notes
- **DEVELOPMENT** - Code, git, CI/CD
- **RESEARCH** - Web search, document analysis
- **AUTOMATION** - Workflows, scheduling
- **DATA** - Database, analytics
- **SYSTEM** - OS operations, file management
- **CREATIVE** - Content generation, design
- **PERSONAL** - Health, finance, habits

## CLI Commands

### Initialize
```bash
jarvis init                    # Detect hardware and setup
jarvis init --preset morning-digest-mac
```

### Skill Management
```bash
# List skills
jarvis skill list
jarvis skill list --category development

# Search skills
jarvis skill search "email"

# Install skills
jarvis skill install hermes:arxiv
jarvis skill install openclaw:web-search
jarvis skill install github:user/repo
jarvis skill install local:./my_skill.py

# Sync from source
jarvis skill sync hermes --category research
jarvis skill sync openclaw
```

### Optimization
```bash
# Optimize from trace history
jarvis optimize skills --policy dspy
jarvis optimize skills --policy rl

# Benchmark performance
jarvis bench skills --max-samples 5 --seeds 42
```

### Usage
```bash
# Ask questions (skills auto-discovered)
jarvis ask "What is the capital of France?"
jarvis ask "Use the code-explainer skill to explain this code"
```

### Diagnostics
```bash
jarvis doctor                  # Check installation
```

## Built-in Skills

### Communication
- **email_intake** - Extract requirements from emails
- **manage_email** - Read, summarize, draft emails
- **email_notifier** - Send notifications

### Development
- **project_architect** - Generate architecture & design
- **code_generator** - Agentic code generation with testing
- **github_automation** - Repo creation, PRs, version control
- **ide_control** - VS Code, package managers, dev servers
- **dev_tools** - Git, npm, docker, boilerplate generation

### Productivity
- **manage_calendar** - Calendar operations
- **set_reminder** - Reminder management
- **daily_brief** - Morning digest

### Research
- **web_search** - Web search with Brave API
- **github_summary** - GitHub activity summaries

### System
- **system_status** - System monitoring
- **system_tools** - File operations, shell commands
- **run_code** - Code execution sandbox

### Creative
- **website_builder** - Website generation
- **file_writer** - File creation
- **music_player** - Music control

### Personal
- **get_weather** - Weather information
- **smart_home** - Home automation

### Workflows
- **project_completion** - Project delivery notifications
- **project_planner** - Project planning

## Skill Discovery

Agents automatically discover skills from the catalog:

```python
from jarvis.skills.skill_catalog import get_catalog

catalog = get_catalog()

# List all skills
skills = catalog.list_skills()

# Filter by category
dev_skills = catalog.list_skills(category="development")

# Search
results = catalog.search_skills("email")

# Get tool definitions for LLM
tools = catalog.get_tool_definitions()
```

## Creating Custom Skills

### 1. Define Skill Spec

```python
from jarvis.skills.skill_standard import create_skill_spec, SkillCategory, SkillType

spec = create_skill_spec(
    name="my_custom_skill",
    description="Does something awesome",
    input_schema={
        "type": "object",
        "properties": {
            "input": {"type": "string"}
        },
        "required": ["input"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "result": {"type": "string"}
        }
    },
    category=SkillCategory.AUTOMATION,
    skill_type=SkillType.TOOL,
    tags=["custom", "automation"],
    cost_estimate="low",
    latency_estimate="fast"
)
```

### 2. Implement Skill

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
                "input": {"type": "string"}
            },
            "required": ["input"]
        }
    
    def execute(self, **kwargs) -> SkillResult:
        input_data = kwargs.get("input")
        
        # Your logic here
        result = f"Processed: {input_data}"
        
        return SkillResult(
            success=True,
            result={"result": result},
            error_message=None,
            execution_time_ms=10
        )
```

### 3. Register Skill

```python
from jarvis.skills.skill_catalog import get_catalog, SkillMetadata

catalog = get_catalog()

metadata = SkillMetadata(
    name="my_custom_skill",
    version="1.0.0",
    description="Does something awesome",
    category="automation",
    author="You",
    tags=["custom"],
    source="local"
)

skill_instance = MyCustomSkill()
catalog.register_skill(skill_instance, metadata)
```

## Skill Sources

### Hermes Agent
~150 curated skills from [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)

```bash
jarvis skill install hermes:arxiv
jarvis skill install hermes:code-explainer
jarvis skill sync hermes --category research
```

### OpenClaw
~13,700 community skills from [openclaw/skills](https://github.com/openclaw/skills)

```bash
jarvis skill install openclaw:web-search
jarvis skill install openclaw:pdf-reader
jarvis skill sync openclaw
```

### GitHub
Any GitHub repository with agentskills.io format

```bash
jarvis skill install github:username/repo
```

### Local
Your own custom skills

```bash
jarvis skill install local:./my_skill.py
```

## Skill Optimization

Improve skills from trace history:

### DSPy Policy
Uses DSPy for prompt optimization

```bash
jarvis optimize skills --policy dspy
```

### RL Policy
Reinforcement learning from user feedback

```bash
jarvis optimize skills --policy rl
```

### Distillation
Distill from larger model traces

```bash
jarvis optimize skills --policy distill
```

## Benchmarking

Measure skill performance:

```bash
# Basic benchmark
jarvis bench skills

# With parameters
jarvis bench skills --max-samples 10 --seeds 42 43 44
```

Metrics tracked:
- **Accuracy** - Task success rate
- **Latency** - Execution time
- **Cost** - API costs
- **Energy** - Power consumption (on-device)

## Interoperability

Skills are compatible with:

- **OpenJarvis** - Via `to_openjarvis_format()`
- **Claude API** - Via `to_claude_format()`
- **OpenAI** - Via `to_openai_format()`
- **Any agentskills.io framework**

```python
spec = SkillSpec(...)

# Convert to different formats
openjarvis_tool = spec.to_openjarvis_format()
claude_tool = spec.to_claude_format()
openai_tool = spec.to_openai_format()
```

## Best Practices

1. **Single Responsibility** - Each skill does one thing well
2. **Clear Inputs/Outputs** - Well-defined JSON schemas
3. **Error Handling** - Graceful failure with error messages
4. **Documentation** - Clear descriptions and examples
5. **Testing** - Unit tests for each skill
6. **Versioning** - Semantic versioning (1.0.0)
7. **Dependencies** - Declare all requirements
8. **Cost Awareness** - Estimate API costs
9. **Latency Awareness** - Estimate execution time
10. **Idempotency** - Same input = same output

## Future Enhancements

- [ ] Skill marketplace
- [ ] Automatic skill composition
- [ ] Skill versioning and updates
- [ ] Skill analytics dashboard
- [ ] Multi-language support (JS, Go, Rust)
- [ ] Skill sandboxing for security
- [ ] Skill caching for performance
- [ ] Skill A/B testing
- [ ] Community skill ratings
- [ ] Skill dependency resolution

## Resources

- [agentskills.io Specification](https://agentskills.io/specification)
- [OpenJarvis Documentation](https://open-jarvis.github.io/OpenJarvis/)
- [Hermes Agent Skills](https://github.com/NousResearch/hermes-agent)
- [OpenClaw Skills](https://github.com/openclaw/skills)
