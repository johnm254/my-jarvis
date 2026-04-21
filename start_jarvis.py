#!/usr/bin/env python3
"""
JARVIS Startup Script
Quick launcher for JARVIS with menu options
"""

import os
import sys
import subprocess
from pathlib import Path


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print JARVIS banner."""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  JARVIS - Your Personal AI Assistant".center(68) + "║")
    print("║" + "  Talk Naturally - Like a Friend".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝\n")


def check_env():
    """Check if .env file exists and has required keys."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("\n📝 Creating .env from .env.example...")
        
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file")
            print("\n⚠️  Please edit .env and add your API keys:")
            print("   - LLM_API_KEY (required) - Get from https://console.groq.com")
            print("   - WEATHER_API_KEY (optional)")
            print("   - GITHUB_TOKEN (optional)")
            print("\nPress Enter to continue...")
            input()
            return False
        else:
            print("❌ .env.example not found!")
            return False
    
    # Check for required keys
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("LLM_API_KEY"):
        print("⚠️  Warning: LLM_API_KEY not set in .env!")
        print("\n📝 Get a free API key from: https://console.groq.com")
        print("   Then add it to .env file:")
        print("   LLM_API_KEY=your_key_here")
        print("\nPress Enter to continue...")
        input()
        return False
    
    return True


def run_script(script_name):
    """Run a Python script."""
    try:
        subprocess.run([sys.executable, script_name], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main menu."""
    while True:
        clear_screen()
        print_banner()
        
        # Check environment
        env_ok = check_env()
        
        if not env_ok:
            print("\n⚠️  Please configure .env file first!")
            print("\nPress Enter to exit...")
            input()
            break
        
        print("Choose an option:\n")
        print("  1. 🚀 Start JARVIS (Conversational Mode)")
        print("  2. 🧪 Quick Test (30 seconds)")
        print("  3. 🎬 Full Demo")
        print("  4. 📋 List All Skills")
        print("  5. 🔧 System Diagnostics")
        print("  6. 📧 Process Email Projects")
        print("  7. 📚 View Documentation")
        print("  8. ❌ Exit")
        print()
        
        choice = input("Enter choice (1-8): ").strip()
        
        if choice == "1":
            clear_screen()
            print("🚀 Starting JARVIS...\n")
            run_script("conversational_jarvis.py")
            
        elif choice == "2":
            clear_screen()
            print("🧪 Running Quick Test...\n")
            run_script("demo_quick_test.py")
            print("\nPress Enter to continue...")
            input()
            
        elif choice == "3":
            clear_screen()
            print("🎬 Running Full Demo...\n")
            run_script("demo_conversational_full.py")
            print("\nPress Enter to continue...")
            input()
            
        elif choice == "4":
            clear_screen()
            print("📋 Listing All Skills...\n")
            run_script("jarvis_cli.py")
            print("\nPress Enter to continue...")
            input()
            
        elif choice == "5":
            clear_screen()
            print("🔧 Running System Diagnostics...\n")
            run_script("diagnose_computer.py")
            print("\nPress Enter to continue...")
            input()
            
        elif choice == "6":
            clear_screen()
            print("📧 Processing Email Projects...\n")
            run_script("process_my_email.py")
            print("\nPress Enter to continue...")
            input()
            
        elif choice == "7":
            clear_screen()
            print("📚 Documentation Files:\n")
            docs = [
                ("Quick Start", "QUICK_START_CONVERSATIONAL_JARVIS.md"),
                ("User Guide", "CONVERSATIONAL_JARVIS_GUIDE.md"),
                ("System Overview", "COMPLETE_SYSTEM_OVERVIEW.md"),
                ("Ready Guide", "CONVERSATIONAL_JARVIS_READY.md"),
            ]
            for name, file in docs:
                print(f"  • {name}: {file}")
            print("\nPress Enter to continue...")
            input()
            
        elif choice == "8":
            clear_screen()
            print("\n👋 Goodbye! JARVIS will be here when you need me.\n")
            break
            
        else:
            print("\n❌ Invalid choice. Press Enter to try again...")
            input()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPress Enter to exit...")
        input()
