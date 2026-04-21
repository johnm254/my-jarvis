"""Skills module - Executable tools and capabilities."""

from jarvis.skills.base import Skill, SkillRegistry, SkillResult
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
from jarvis.skills.code_generator import CodeGeneratorSkill
from jarvis.skills.project_planner import ProjectPlannerSkill
from jarvis.skills.website_builder import WebsiteBuilderSkill
from jarvis.skills.file_writer import FileWriterSkill
from jarvis.skills.system_tools import SystemToolsSkill
from jarvis.skills.email_notifier import EmailNotifierSkill
from jarvis.skills.music_player import MusicPlayerSkill
from jarvis.skills.dev_tools import DevToolsSkill
from jarvis.skills.email_intake import EmailIntakeSkill
from jarvis.skills.project_architect import ProjectArchitectSkill
from jarvis.skills.github_automation import GitHubAutomationSkill
from jarvis.skills.ide_control import IDEControlSkill
from jarvis.skills.project_completion import ProjectCompletionSkill
from jarvis.skills.computer_diagnostics import ComputerDiagnosticsSkill
from jarvis.skills.system_optimizer import SystemOptimizerSkill

__all__ = [
    "Skill", "SkillRegistry", "SkillResult",
    "WebSearchSkill", "GetWeatherSkill", "SystemStatusSkill",
    "RunCodeSkill", "ManageCalendarSkill", "ManageEmailSkill",
    "SmartHomeSkill", "GitHubSummarySkill", "DailyBriefSkill",
    "SetReminderSkill", "CodeGeneratorSkill", "ProjectPlannerSkill",
    "WebsiteBuilderSkill", "FileWriterSkill",
    "SystemToolsSkill", "EmailNotifierSkill", "MusicPlayerSkill",
    "DevToolsSkill",
    "EmailIntakeSkill", "ProjectArchitectSkill", "GitHubAutomationSkill",
    "IDEControlSkill", "ProjectCompletionSkill",
    "ComputerDiagnosticsSkill", "SystemOptimizerSkill",
]
