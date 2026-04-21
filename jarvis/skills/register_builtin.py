"""Register all built-in JARVIS skills with the catalog."""

from jarvis.skills.skill_catalog import get_catalog, SkillMetadata

# Import all built-in skills
from jarvis.skills.email_intake import EmailIntakeSkill
from jarvis.skills.project_architect import ProjectArchitectSkill
from jarvis.skills.code_generator import CodeGeneratorSkill
from jarvis.skills.github_automation import GitHubAutomationSkill
from jarvis.skills.ide_control import IDEControlSkill
from jarvis.skills.project_completion import ProjectCompletionSkill
from jarvis.skills.dev_tools import DevToolsSkill
from jarvis.skills.web_search import WebSearchSkill
from jarvis.skills.get_weather import GetWeatherSkill
from jarvis.skills.system_status import SystemStatusSkill
from jarvis.skills.run_code import RunCodeSkill
from jarvis.skills.manage_calendar import ManageCalendarSkill
from jarvis.skills.manage_email import ManageEmailSkill
from jarvis.skills.smart_home import SmartHomeSkill
from jarvis.skills.github_summary import GitHubSummarySkill
from jarvis.skills.daily_brief import DailyBriefSkill
from jarvis.skills.set_reminder import SetReminderSkill
from jarvis.skills.project_planner import ProjectPlannerSkill
from jarvis.skills.website_builder import WebsiteBuilderSkill
from jarvis.skills.file_writer import FileWriterSkill
from jarvis.skills.system_tools import SystemToolsSkill
from jarvis.skills.email_notifier import EmailNotifierSkill
from jarvis.skills.music_player import MusicPlayerSkill
from jarvis.skills.computer_diagnostics import ComputerDiagnosticsSkill
from jarvis.skills.system_optimizer import SystemOptimizerSkill
from jarvis.skills.computer_control import ComputerControlSkill


def register_all_builtin_skills():
    """Register all built-in skills with the catalog."""
    catalog = get_catalog()
    
    skills = [
        # Full-stack automation skills
        (EmailIntakeSkill(), SkillMetadata(
            name="email_intake",
            version="1.0.0",
            description="Extract structured requirements from project emails using LLM",
            category="communication",
            author="JARVIS",
            tags=["email", "requirements", "parsing", "automation"],
            source="builtin"
        )),
        (ProjectArchitectSkill(), SkillMetadata(
            name="project_architect",
            version="1.0.0",
            description="Generate project architecture, ERD, API specs, and implementation plan",
            category="development",
            author="JARVIS",
            tags=["architecture", "design", "planning", "diagrams"],
            source="builtin"
        )),
        (CodeGeneratorSkill(), SkillMetadata(
            name="code_generator",
            version="1.0.0",
            description="Agentic code generation with iterative testing, linting, and auto-fixing",
            category="development",
            author="JARVIS",
            tags=["codegen", "testing", "linting", "automation"],
            source="builtin"
        )),
        (GitHubAutomationSkill(), SkillMetadata(
            name="github_automation",
            version="1.0.0",
            description="Automate GitHub operations: repos, branches, PRs, version control",
            category="development",
            author="JARVIS",
            tags=["github", "git", "version-control", "automation"],
            source="builtin"
        )),
        (IDEControlSkill(), SkillMetadata(
            name="ide_control",
            version="1.0.0",
            description="Control local development environment: VS Code, package managers, dev servers",
            category="development",
            author="JARVIS",
            tags=["ide", "vscode", "environment", "automation"],
            source="builtin"
        )),
        (ProjectCompletionSkill(), SkillMetadata(
            name="project_completion",
            version="1.0.0",
            description="Send project completion notifications with summary and links",
            category="communication",
            author="JARVIS",
            tags=["notification", "email", "completion", "reporting"],
            source="builtin"
        )),
        
        # Development tools
        (DevToolsSkill(), SkillMetadata(
            name="dev_tools",
            version="1.0.0",
            description="Full-stack developer automation: git, npm, docker, boilerplate generation",
            category="development",
            author="JARVIS",
            tags=["git", "npm", "docker", "cli", "automation"],
            source="builtin"
        )),
        
        # System management
        (ComputerDiagnosticsSkill(), SkillMetadata(
            name="computer_diagnostics",
            version="1.0.0",
            description="Comprehensive computer diagnostics: hardware, software, network, security",
            category="system",
            author="JARVIS",
            tags=["diagnostics", "hardware", "monitoring", "health"],
            source="builtin"
        )),
        (SystemOptimizerSkill(), SkillMetadata(
            name="system_optimizer",
            version="1.0.0",
            description="Optimize computer: clean temp files, clear cache, free disk space",
            category="system",
            author="JARVIS",
            tags=["optimization", "cleanup", "performance", "disk"],
            source="builtin"
        )),
        (SystemStatusSkill(), SkillMetadata(
            name="system_status",
            version="1.0.0",
            description="Monitor system resources: CPU, memory, disk, network",
            category="system",
            author="JARVIS",
            tags=["monitoring", "system", "resources"],
            source="builtin"
        )),
        (SystemToolsSkill(), SkillMetadata(
            name="system_tools",
            version="1.0.0",
            description="System operations: file management, shell commands",
            category="system",
            author="JARVIS",
            tags=["files", "shell", "system"],
            source="builtin"
        )),
        (RunCodeSkill(), SkillMetadata(
            name="run_code",
            version="1.0.0",
            description="Execute code in sandboxed environment",
            category="system",
            author="JARVIS",
            tags=["code", "execution", "sandbox"],
            source="builtin"
        )),
        
        # Communication
        (ManageEmailSkill(), SkillMetadata(
            name="manage_email",
            version="1.0.0",
            description="Manage Gmail: read, summarize, draft messages",
            category="communication",
            author="JARVIS",
            tags=["email", "gmail", "communication"],
            source="builtin"
        )),
        (EmailNotifierSkill(), SkillMetadata(
            name="email_notifier",
            version="1.0.0",
            description="Send email notifications and reports",
            category="communication",
            author="JARVIS",
            tags=["email", "notification", "smtp"],
            source="builtin"
        )),
        
        # Productivity
        (ManageCalendarSkill(), SkillMetadata(
            name="manage_calendar",
            version="1.0.0",
            description="Manage Google Calendar: events, scheduling",
            category="productivity",
            author="JARVIS",
            tags=["calendar", "scheduling", "events"],
            source="builtin"
        )),
        (SetReminderSkill(), SkillMetadata(
            name="set_reminder",
            version="1.0.0",
            description="Set and manage reminders",
            category="productivity",
            author="JARVIS",
            tags=["reminders", "tasks", "notifications"],
            source="builtin"
        )),
        (DailyBriefSkill(), SkillMetadata(
            name="daily_brief",
            version="1.0.0",
            description="Generate daily briefing from email, calendar, and news",
            category="productivity",
            author="JARVIS",
            tags=["briefing", "summary", "daily"],
            source="builtin"
        )),
        (ProjectPlannerSkill(), SkillMetadata(
            name="project_planner",
            version="1.0.0",
            description="Plan and organize projects",
            category="productivity",
            author="JARVIS",
            tags=["planning", "projects", "organization"],
            source="builtin"
        )),
        (FileWriterSkill(), SkillMetadata(
            name="file_writer",
            version="1.0.0",
            description="Create and write files",
            category="productivity",
            author="JARVIS",
            tags=["files", "writing", "creation"],
            source="builtin"
        )),
        
        # Research
        (WebSearchSkill(), SkillMetadata(
            name="web_search",
            version="1.0.0",
            description="Search the web using Brave Search API",
            category="research",
            author="JARVIS",
            tags=["search", "web", "research"],
            source="builtin"
        )),
        (GitHubSummarySkill(), SkillMetadata(
            name="github_summary",
            version="1.0.0",
            description="Summarize GitHub activity and repositories",
            category="research",
            author="JARVIS",
            tags=["github", "summary", "activity"],
            source="builtin"
        )),
        
        # Personal
        (GetWeatherSkill(), SkillMetadata(
            name="get_weather",
            version="1.0.0",
            description="Get weather information for any location",
            category="personal",
            author="JARVIS",
            tags=["weather", "forecast", "location"],
            source="builtin"
        )),
        (SmartHomeSkill(), SkillMetadata(
            name="smart_home",
            version="1.0.0",
            description="Control smart home devices via Home Assistant",
            category="personal",
            author="JARVIS",
            tags=["smart-home", "automation", "iot"],
            source="builtin"
        )),
        (MusicPlayerSkill(), SkillMetadata(
            name="music_player",
            version="1.0.0",
            description="Control music playback",
            category="personal",
            author="JARVIS",
            tags=["music", "audio", "playback"],
            source="builtin"
        )),
        (ComputerControlSkill(), SkillMetadata(
            name="computer_control",
            version="1.0.0",
            description="Full computer control: keyboard, mouse, navigation, typing, file management",
            category="system",
            author="JARVIS",
            tags=["control", "keyboard", "mouse", "navigation", "automation"],
            source="builtin"
        )),
        
        # Creative
        (WebsiteBuilderSkill(), SkillMetadata(
            name="website_builder",
            version="1.0.0",
            description="Generate websites and web pages",
            category="creative",
            author="JARVIS",
            tags=["website", "web", "html", "generation"],
            source="builtin"
        )),
    ]
    
    for skill_instance, metadata in skills:
        catalog.register_skill(skill_instance, metadata)
    
    print(f"✅ Registered {len(skills)} built-in skills")


if __name__ == "__main__":
    register_all_builtin_skills()
