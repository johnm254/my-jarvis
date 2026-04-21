"""Demo script for Preference Learning Hook.

This script demonstrates how the preference learning hook works:
1. Simulates a conversation turn
2. Triggers the preference learning hook
3. Shows extracted preferences, corrections, and facts
4. Displays updated Personal_Profile
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add jarvis to path
sys.path.insert(0, os.path.dirname(__file__))

from jarvis.config import Configuration
from jarvis.brain.brain import Brain
from jarvis.memory.memory_system import MemorySystem
from jarvis.hooks.hooks_engine import HooksEngine
from jarvis.hooks.preference_learning_hook import create_preference_learning_hook


def main():
    """Run the preference learning hook demo."""
    print("=" * 80)
    print("JARVIS Preference Learning Hook Demo")
    print("=" * 80)
    print()
    
    # Initialize configuration
    print("Initializing JARVIS components...")
    config = Configuration(
        llm_model=os.getenv("LLM_MODEL", "claude-sonnet-4-20250514"),
        llm_api_key=os.getenv("CLAUDE_API_KEY", ""),
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_key=os.getenv("SUPABASE_KEY", ""),
        voice_enabled=False,
        wake_word="Hey Jarvis",
        stt_model="whisper",
        tts_api_key="",
        dashboard_port=3000,
        jwt_secret="demo_secret",
        log_level="INFO"
    )
    
    # Initialize components
    memory_system = MemorySystem(config)
    brain = Brain(config)
    hooks_engine = HooksEngine()
    
    # Create and register the preference learning hook
    print("Registering preference learning hook...")
    preference_learning = create_preference_learning_hook(
        hooks_engine=hooks_engine,
        brain=brain,
        memory_system=memory_system,
        user_id="demo_user"
    )
    print("✓ Preference learning hook registered\n")
    
    # Get initial profile
    print("Initial Personal Profile:")
    print("-" * 80)
    initial_profile = memory_system.get_personal_profile("demo_user")
    print(f"Name: {initial_profile.first_name}")
    print(f"Timezone: {initial_profile.timezone}")
    print(f"Communication Style: {initial_profile.communication_style}")
    print(f"Preferences: {initial_profile.preferences}")
    print()
    
    # Simulate conversation scenarios
    scenarios = [
        {
            "name": "User expresses preference",
            "user_input": "I prefer to be called Alex instead of Boss",
            "brain_response": "Understood, I'll call you Alex from now on."
        },
        {
            "name": "User provides work information",
            "user_input": "I work as a software engineer at TechCorp, my hours are 9am to 6pm",
            "brain_response": "Got it! I've noted that you're a software engineer at TechCorp with work hours from 9am to 6pm."
        },
        {
            "name": "User corrects JARVIS",
            "user_input": "Actually, I said I wanted the meeting at 3pm, not 2pm",
            "brain_response": "My apologies for the confusion. I'll update the meeting to 3pm."
        },
        {
            "name": "User shares interests",
            "user_input": "I'm really into machine learning and AI research",
            "brain_response": "That's great! Machine learning and AI research are fascinating fields."
        }
    ]
    
    # Process each scenario
    for i, scenario in enumerate(scenarios, 1):
        print(f"Scenario {i}: {scenario['name']}")
        print("-" * 80)
        print(f"User: {scenario['user_input']}")
        print(f"JARVIS: {scenario['brain_response']}")
        print()
        
        # Trigger the preference learning hook
        print("Triggering preference learning hook...")
        preference_learning.execute(
            user_input=scenario['user_input'],
            brain_response=scenario['brain_response'],
            session_id=f"demo_session_{i}"
        )
        print("✓ Preference learning completed\n")
    
    # Get updated profile
    print("Updated Personal Profile:")
    print("-" * 80)
    updated_profile = memory_system.get_personal_profile("demo_user")
    print(f"Name: {updated_profile.first_name}")
    print(f"Timezone: {updated_profile.timezone}")
    print(f"Communication Style: {updated_profile.communication_style}")
    print(f"\nPreferences ({len(updated_profile.preferences)} items):")
    for key, value in updated_profile.preferences.items():
        print(f"  - {key}: {value}")
    print()
    
    # Show how the hook is registered
    print("Registered Hooks:")
    print("-" * 80)
    all_hooks = hooks_engine.list_all_hooks()
    for hook in all_hooks:
        print(f"  - {hook.name} (ID: {hook.id})")
        print(f"    Type: {hook.hook_type}")
        print(f"    Trigger: {hook.trigger}")
        print(f"    Enabled: {hook.enabled}")
        print()
    
    print("=" * 80)
    print("Demo completed!")
    print()
    print("Key Features Demonstrated:")
    print("  ✓ Preference extraction from conversations")
    print("  ✓ Correction detection and storage")
    print("  ✓ Fact learning about the user")
    print("  ✓ Personal_Profile updates")
    print("  ✓ Event-based hook registration")
    print("=" * 80)
    
    # Cleanup
    hooks_engine.shutdown()
    memory_system.close()


if __name__ == "__main__":
    main()
