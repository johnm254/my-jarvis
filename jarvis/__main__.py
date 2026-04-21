"""Main entry point for JARVIS Personal AI Assistant.

This module initializes and wires together all JARVIS components:
- Configuration from environment
- Memory System with Supabase connection
- Brain with Claude API and Memory System
- Skill Registry with all skills
- Hooks Engine with all hooks
- Voice Interface with wake word detection
- CLI Interface
- Dashboard backend

Validates: Requirements 19.1, 19.2, 19.3, 19.4
"""

import argparse
import logging
import sys
from pathlib import Path

from jarvis.config import load_config
from jarvis.logging_config import setup_logging
from jarvis.memory.memory_system import MemorySystem
from jarvis.brain.brain import Brain
from jarvis.skills.base import SkillRegistry
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
from jarvis.hooks.hooks_engine import HooksEngine
from jarvis.hooks.morning_brief_hook import register_morning_brief_hook
from jarvis.hooks.preference_learning_hook import register_preference_learning_hook
from jarvis.hooks.calendar_reminder_hook import register_calendar_reminder_hook
from jarvis.hooks.reminder_delivery_hook import register_reminder_delivery_hook

logger = logging.getLogger(__name__)


class JarvisApplication:
    """
    Main JARVIS application that wires all components together.
    
    Initializes:
    - Configuration from environment
    - Memory System with Supabase
    - Brain with Claude API
    - Skill Registry with all skills
    - Hooks Engine with all hooks
    - Voice Interface (optional)
    - CLI Interface
    - Dashboard backend
    """
    
    def __init__(self):
        """Initialize the JARVIS application."""
        self.config = None
        self.memory_system = None
        self.brain = None
        self.skill_registry = None
        self.hooks_engine = None
        self.voice_interface = None
    
    def initialize(self):
        """Initialize all JARVIS components."""
        logger.info("Initializing JARVIS Personal AI Assistant...")
        
        # 1. Load configuration from environment
        logger.info("Loading configuration from environment...")
        self.config = load_config()
        logger.info(f"Configuration loaded: LLM model={self.config.llm_model}, Dashboard port={self.config.dashboard_port}")
        
        # 2. Initialize Memory System with Supabase connection
        logger.info("Initializing Memory System...")
        self.memory_system = MemorySystem(self.config)
        logger.info("Memory System initialized successfully")
        
        # 3. Initialize Skill Registry and register all skills
        logger.info("Initializing Skill Registry...")
        self.skill_registry = SkillRegistry()
        self._register_skills()
        logger.info(f"Skill Registry initialized with {len(self.skill_registry.list_skills())} skills")
        
        # 4. Initialize Brain with Claude API and Memory System
        logger.info("Initializing Brain...")
        self.brain = Brain(self.config, self.skill_registry)
        logger.info("Brain initialized successfully")
        
        # 5. Initialize Hooks Engine and register all hooks
        logger.info("Initializing Hooks Engine...")
        self.hooks_engine = HooksEngine(self.memory_system, self.brain)
        self._register_hooks()
        logger.info(f"Hooks Engine initialized with {len(self.hooks_engine.list_active_hooks())} hooks")
        
        # 6. Initialize Voice Interface (if enabled)
        if self.config.voice_enabled:
            logger.info("Voice interface is enabled in configuration")
            try:
                from jarvis.voice.voice_interface import VoiceInterface
                self.voice_interface = VoiceInterface(
                    model_name=self.config.stt_model,
                    elevenlabs_api_key=self.config.tts_api_key
                )
                logger.info("Voice Interface initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Voice Interface: {e}")
                logger.warning("Continuing without voice support")
        else:
            logger.info("Voice interface is disabled in configuration")
        
        logger.info("JARVIS initialization complete!")
    
    def _register_skills(self):
        """Register all available skills."""
        skills = [
            WebSearchSkill(self.config),
            GetWeatherSkill(self.config),
            SystemStatusSkill(),
            RunCodeSkill(),
            ManageCalendarSkill(self.config),
            ManageEmailSkill(self.config),
            SmartHomeSkill(self.config),
            GitHubSummarySkill(self.config),
            DailyBriefSkill(self.brain, self.skill_registry),
            SetReminderSkill(self.memory_system),
        ]
        
        for skill in skills:
            self.skill_registry.register_skill(skill)
            logger.debug(f"Registered skill: {skill.name}")
    
    def _register_hooks(self):
        """Register all automated hooks."""
        # Morning Brief Hook (daily at 7:00 AM)
        register_morning_brief_hook(self.hooks_engine, self.brain, self.skill_registry)
        
        # Preference Learning Hook (after every conversation)
        register_preference_learning_hook(self.hooks_engine, self.memory_system, self.brain)
        
        # Calendar Reminder Hook (every 5 minutes)
        register_calendar_reminder_hook(self.hooks_engine, self.skill_registry, self.voice_interface)
        
        # Reminder Delivery Hook (every 1 minute)
        register_reminder_delivery_hook(self.hooks_engine, self.memory_system, self.voice_interface)
        
        logger.debug("All hooks registered successfully")
    
    def start_cli(self):
        """Start the CLI interface."""
        logger.info("Starting CLI interface...")
        from jarvis.cli.cli_interface import CLIInterface
        
        cli = CLIInterface(self.brain, self.memory_system)
        cli.run()
    
    def start_dashboard(self, host: str = '0.0.0.0', port: int = None, debug: bool = False):
        """Start the dashboard backend server."""
        logger.info("Starting Dashboard backend...")
        from jarvis.dashboard.app import run_server
        
        if port is None:
            port = self.config.dashboard_port
        
        run_server(host=host, port=port, debug=debug)
    
    def start_voice(self):
        """Start the voice interface."""
        if not self.voice_interface:
            logger.error("Voice interface not initialized. Enable voice in configuration.")
            return
        
        logger.info("Starting Voice interface...")
        # TODO: Implement voice interaction loop
        logger.warning("Voice interface loop not yet implemented")
    
    def shutdown(self):
        """Shutdown JARVIS and cleanup resources."""
        logger.info("Shutting down JARVIS...")
        
        if self.hooks_engine:
            self.hooks_engine.shutdown()
        
        if self.memory_system:
            self.memory_system.close()
        
        logger.info("JARVIS shutdown complete")


def main():
    """Main entry point for JARVIS application."""
    parser = argparse.ArgumentParser(
        description="JARVIS Personal AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m jarvis cli              Start CLI interface
  python -m jarvis dashboard        Start web dashboard
  python -m jarvis voice            Start voice interface
  python -m jarvis --help           Show this help message
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['cli', 'dashboard', 'voice'],
        help='Interface mode to start'
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host address for dashboard (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        help='Port for dashboard (default: from config)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set logging level (overrides config)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = args.log_level if args.log_level else None
    setup_logging(log_level=log_level)
    
    # Create and initialize JARVIS application
    app = JarvisApplication()
    
    try:
        app.initialize()
        
        # Start the requested interface
        if args.mode == 'cli':
            app.start_cli()
        elif args.mode == 'dashboard':
            app.start_dashboard(host=args.host, port=args.port, debug=args.debug)
        elif args.mode == 'voice':
            app.start_voice()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        app.shutdown()


if __name__ == '__main__':
    main()
