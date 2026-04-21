"""
Comprehensive Demo of Conversational JARVIS
Shows all features in action
"""

import os
import time
from dotenv import load_dotenv
from conversational_jarvis import ConversationalJARVIS

load_dotenv()


def demo_conversation():
    """Run a comprehensive demo conversation."""
    print("\n" + "="*70)
    print("🤖 CONVERSATIONAL JARVIS - COMPREHENSIVE DEMO")
    print("="*70 + "\n")
    
    print("This demo shows JARVIS having natural conversations")
    print("and performing various tasks.\n")
    
    # Initialize JARVIS in text mode
    jarvis = ConversationalJARVIS(voice_enabled=False)
    
    # Demo scenarios
    scenarios = [
        {
            "name": "🎭 Natural Greeting",
            "inputs": [
                "Hello JARVIS",
                "How are you today?",
            ]
        },
        {
            "name": "💬 Casual Conversation",
            "inputs": [
                "What can you help me with?",
                "That sounds great!",
            ]
        },
        {
            "name": "⏰ Time & Date",
            "inputs": [
                "What time is it?",
                "What's the date today?",
            ]
        },
        {
            "name": "🎵 Music Control",
            "inputs": [
                "Play some music",
                "Play Despacito",
            ]
        },
        {
            "name": "💻 Application Control",
            "inputs": [
                "Open Calculator",
                "Open Notepad",
            ]
        },
        {
            "name": "🔧 System Diagnostics",
            "inputs": [
                "Check my computer health",
                "How much disk space do I have?",
            ]
        },
        {
            "name": "🧹 System Optimization",
            "inputs": [
                "My computer is slow",
                "Can you clean it up?",
            ]
        },
        {
            "name": "🎯 Context Memory",
            "inputs": [
                "I need help with something",
                "Actually, never mind",
                "Thanks anyway",
            ]
        },
        {
            "name": "👋 Goodbye",
            "inputs": [
                "Thanks for everything",
                "Goodbye JARVIS",
            ]
        }
    ]
    
    for scenario in scenarios:
        print("\n" + "-"*70)
        print(f"\n{scenario['name']}")
        print("-"*70 + "\n")
        
        for user_input in scenario['inputs']:
            print(f"👤 You: {user_input}")
            jarvis.handle_conversation(user_input.lower())
            print()
            time.sleep(0.5)  # Pause between messages
            
            if not jarvis.listening:
                break
        
        if not jarvis.listening:
            break
        
        time.sleep(1)  # Pause between scenarios
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETE!")
    print("="*70 + "\n")
    
    print("📊 Demo Summary:")
    print("  ✅ Natural greetings and conversations")
    print("  ✅ Time and date information")
    print("  ✅ Music playback control")
    print("  ✅ Application launching")
    print("  ✅ System diagnostics")
    print("  ✅ System optimization")
    print("  ✅ Context memory and follow-ups")
    print("  ✅ Friendly personality")
    print()
    print("🎤 To use with voice:")
    print("   python conversational_jarvis.py")
    print()


def demo_features():
    """Show individual feature demos."""
    print("\n" + "="*70)
    print("🔧 FEATURE DEMONSTRATIONS")
    print("="*70 + "\n")
    
    jarvis = ConversationalJARVIS(voice_enabled=False)
    
    features = [
        {
            "name": "🎵 Music Player",
            "description": "Play any song on YouTube with auto-play",
            "commands": [
                "Play Despacito",
                "Play Shape of You by Ed Sheeran",
                "Play relaxing music",
            ]
        },
        {
            "name": "💻 App Launcher",
            "description": "Open any application on your computer",
            "commands": [
                "Open Chrome",
                "Open Calculator",
                "Open Notepad",
                "Open VS Code",
            ]
        },
        {
            "name": "🔍 File Finder",
            "description": "Search and open files/folders",
            "commands": [
                "Open my documents",
                "Open downloads folder",
                "Open desktop",
            ]
        },
        {
            "name": "🔧 System Tools",
            "description": "Diagnose and optimize your computer",
            "commands": [
                "Check my computer",
                "Clean up my system",
                "Free up disk space",
            ]
        },
        {
            "name": "ℹ️ Information",
            "description": "Get current information",
            "commands": [
                "What time is it?",
                "What's the date?",
                "What's the weather?",
            ]
        },
    ]
    
    for feature in features:
        print(f"\n{feature['name']}")
        print(f"Description: {feature['description']}")
        print("\nExample commands:")
        for cmd in feature['commands']:
            print(f"  • {cmd}")
        print()
    
    print("="*70)
    print("💡 Try any of these commands with JARVIS!")
    print("="*70 + "\n")


def demo_personality():
    """Show JARVIS personality traits."""
    print("\n" + "="*70)
    print("🎭 JARVIS PERSONALITY DEMO")
    print("="*70 + "\n")
    
    jarvis = ConversationalJARVIS(voice_enabled=False)
    
    print("JARVIS has a friendly, helpful personality:\n")
    
    personality_tests = [
        ("Friendly", "Hello JARVIS, nice to meet you"),
        ("Professional", "I need help with my computer"),
        ("Witty", "You're pretty smart"),
        ("Proactive", "My disk is almost full"),
        ("Context-Aware", "What did I just ask about?"),
    ]
    
    for trait, test_input in personality_tests:
        print(f"\n{trait} Response:")
        print(f"👤 You: {test_input}")
        jarvis.handle_conversation(test_input.lower())
        print()
        time.sleep(0.5)
    
    print("="*70)
    print("✅ JARVIS has a natural, friendly personality!")
    print("="*70 + "\n")


def main():
    """Main demo menu."""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  CONVERSATIONAL JARVIS - COMPREHENSIVE DEMO".center(68) + "║")
    print("║" + "  Talk Naturally - Like a Friend".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝\n")
    
    print("Choose a demo:\n")
    print("  1. Full Conversation Demo (Recommended)")
    print("  2. Feature Demonstrations")
    print("  3. Personality Demo")
    print("  4. Run All Demos")
    print("  5. Exit")
    print()
    
    choice = input("Enter choice (1-5): ").strip()
    
    if choice == "1":
        demo_conversation()
    elif choice == "2":
        demo_features()
    elif choice == "3":
        demo_personality()
    elif choice == "4":
        demo_conversation()
        time.sleep(2)
        demo_features()
        time.sleep(2)
        demo_personality()
    else:
        print("\n👋 Goodbye!")
        return
    
    print("\n🎉 Want to try JARVIS yourself?")
    print("   Run: python conversational_jarvis.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  - LLM_API_KEY in .env file")
        print("  - All dependencies installed")
        print("  - Internet connection")
