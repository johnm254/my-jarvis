#!/usr/bin/env python3
"""
JARVIS CLI - OpenJarvis-style command interface

Usage:
    jarvis init                          # Initialize and detect hardware
    jarvis ask "question"                # Ask a question
    jarvis skill install hermes:arxiv    # Install skill from Hermes
    jarvis skill list                    # List installed skills
    jarvis skill sync hermes --category research
    jarvis optimize skills --policy dspy # Optimize from traces
    jarvis bench skills                  # Benchmark skills
    jarvis doctor                        # Diagnose issues
"""

import sys
import argparse
import logging
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent))

from jarvis.skills.skill_catalog import get_catalog, SkillMetadata
from jarvis.skills.skill_standard import SkillCategory, SkillType
from jarvis.config import load_config

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def cmd_init(args):
    """Initialize JARVIS and detect hardware."""
    print("🤖 Initializing JARVIS...")
    print()
    
    # Detect hardware
    print("🔍 Detecting hardware...")
    import platform
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Python: {platform.python_version()}")
    print(f"   Architecture: {platform.machine()}")
    
    # Check for GPU
    try:
        import torch
        if torch.cuda.is_available():
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("   GPU: Not available")
    except ImportError:
        print("   GPU: PyTorch not installed")
    
    print()
    print("✅ JARVIS initialized successfully!")
    print()
    print("Next steps:")
    print("  1. jarvis skill list                    # See available skills")
    print("  2. jarvis ask 'What can you do?'        # Ask a question")
    print("  3. jarvis skill install hermes:arxiv    # Install more skills")


def cmd_ask(args):
    """Ask JARVIS a question."""
    question = args.question
    print(f"🤔 Question: {question}")
    print()
    
    # TODO: Integrate with Brain for actual question answering
    print("💡 Answer: This would use the Brain module to answer your question.")
    print("   Integration with LLM and skills coming soon!")


def cmd_skill_install(args):
    """Install a skill from external source."""
    source = args.source
    print(f"📦 Installing skill from: {source}")
    
    catalog = get_catalog()
    try:
        success = catalog.install_skill(source)
        if success:
            print(f"✅ Skill installed successfully!")
        else:
            print(f"⚠️  Skill installation not yet implemented for this source")
    except Exception as e:
        print(f"❌ Error: {e}")


def cmd_skill_list(args):
    """List installed skills."""
    catalog = get_catalog()
    skills = catalog.list_skills(category=args.category)
    
    if not skills:
        print("No skills installed yet.")
        print()
        print("Install skills with:")
        print("  jarvis skill install hermes:arxiv")
        print("  jarvis skill install openclaw:web-search")
        return
    
    print(f"📚 Installed Skills ({len(skills)}):")
    print()
    
    # Group by category
    by_category = {}
    for skill in skills:
        cat = skill.category
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(skill)
    
    for category, cat_skills in sorted(by_category.items()):
        print(f"  {category.upper()}")
        for skill in cat_skills:
            tags_str = ", ".join(skill.tags) if skill.tags else ""
            print(f"    • {skill.name} v{skill.version}")
            print(f"      {skill.description}")
            if tags_str:
                print(f"      Tags: {tags_str}")
            print()


def cmd_skill_sync(args):
    """Sync skills from a source."""
    source = args.source
    category = args.category
    
    print(f"🔄 Syncing skills from {source}")
    if category:
        print(f"   Category: {category}")
    
    catalog = get_catalog()
    catalog.sync_skills(source, category)


def cmd_skill_search(args):
    """Search for skills."""
    query = args.query
    print(f"🔍 Searching for: {query}")
    print()
    
    catalog = get_catalog()
    results = catalog.search_skills(query)
    
    if not results:
        print("No skills found.")
        return
    
    print(f"Found {len(results)} skill(s):")
    print()
    
    for skill in results:
        print(f"  • {skill.name} v{skill.version}")
        print(f"    {skill.description}")
        print(f"    Category: {skill.category} | Source: {skill.source}")
        print()


def cmd_optimize(args):
    """Optimize skills from trace history."""
    policy = args.policy
    print(f"🎯 Optimizing skills with policy: {policy}")
    
    catalog = get_catalog()
    catalog.optimize_skills(policy)


def cmd_bench(args):
    """Benchmark skill performance."""
    max_samples = args.max_samples
    seeds = args.seeds
    
    print(f"📊 Benchmarking skills...")
    print(f"   Max samples: {max_samples}")
    if seeds:
        print(f"   Seeds: {seeds}")
    
    catalog = get_catalog()
    catalog.benchmark_skills(max_samples, seeds)


def cmd_doctor(args):
    """Diagnose JARVIS installation."""
    print("🏥 Running diagnostics...")
    print()
    
    issues = []
    
    # Check Python version
    import sys
    if sys.version_info < (3, 10):
        issues.append("Python 3.10+ required")
    else:
        print("✅ Python version OK")
    
    # Check config
    try:
        config = load_config()
        print("✅ Configuration loaded")
    except Exception as e:
        issues.append(f"Configuration error: {e}")
        print(f"❌ Configuration error: {e}")
    
    # Check skills directory
    catalog = get_catalog()
    skills = catalog.list_skills()
    print(f"✅ Skills directory OK ({len(skills)} skills)")
    
    # Check dependencies
    deps = {
        "anthropic": "LLM API",
        "supabase": "Memory system",
        "fastapi": "Dashboard server"
    }
    
    for module, purpose in deps.items():
        try:
            __import__(module)
            print(f"✅ {module} installed ({purpose})")
        except ImportError:
            issues.append(f"{module} not installed ({purpose})")
            print(f"⚠️  {module} not installed ({purpose})")
    
    print()
    if issues:
        print(f"❌ Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("✅ All checks passed!")


def main():
    parser = argparse.ArgumentParser(
        description="JARVIS - Personal AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # jarvis init
    parser_init = subparsers.add_parser('init', help='Initialize JARVIS')
    parser_init.add_argument('--preset', help='Use a preset configuration')
    parser_init.set_defaults(func=cmd_init)
    
    # jarvis ask
    parser_ask = subparsers.add_parser('ask', help='Ask a question')
    parser_ask.add_argument('question', help='Question to ask')
    parser_ask.set_defaults(func=cmd_ask)
    
    # jarvis skill
    parser_skill = subparsers.add_parser('skill', help='Manage skills')
    skill_subparsers = parser_skill.add_subparsers(dest='skill_command')
    
    # jarvis skill install
    skill_install = skill_subparsers.add_parser('install', help='Install a skill')
    skill_install.add_argument('source', help='Source (hermes:name, openclaw:name, github:user/repo)')
    skill_install.set_defaults(func=cmd_skill_install)
    
    # jarvis skill list
    skill_list = skill_subparsers.add_parser('list', help='List installed skills')
    skill_list.add_argument('--category', help='Filter by category')
    skill_list.set_defaults(func=cmd_skill_list)
    
    # jarvis skill sync
    skill_sync = skill_subparsers.add_parser('sync', help='Sync skills from source')
    skill_sync.add_argument('source', help='Source to sync from')
    skill_sync.add_argument('--category', help='Filter by category')
    skill_sync.set_defaults(func=cmd_skill_sync)
    
    # jarvis skill search
    skill_search = skill_subparsers.add_parser('search', help='Search for skills')
    skill_search.add_argument('query', help='Search query')
    skill_search.set_defaults(func=cmd_skill_search)
    
    # jarvis optimize
    parser_optimize = subparsers.add_parser('optimize', help='Optimize skills')
    parser_optimize.add_argument('target', choices=['skills'], help='What to optimize')
    parser_optimize.add_argument('--policy', default='dspy', help='Optimization policy')
    parser_optimize.set_defaults(func=cmd_optimize)
    
    # jarvis bench
    parser_bench = subparsers.add_parser('bench', help='Benchmark performance')
    parser_bench.add_argument('target', choices=['skills'], help='What to benchmark')
    parser_bench.add_argument('--max-samples', type=int, default=5, help='Max samples')
    parser_bench.add_argument('--seeds', type=int, nargs='+', help='Random seeds')
    parser_bench.set_defaults(func=cmd_bench)
    
    # jarvis doctor
    parser_doctor = subparsers.add_parser('doctor', help='Diagnose issues')
    parser_doctor.set_defaults(func=cmd_doctor)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
