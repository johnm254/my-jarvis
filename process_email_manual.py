"""
Manual Email Processing Script

Use this to process project requirement emails manually until
Gmail API integration is complete.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from jarvis.skills.email_intake import EmailIntakeSkill
from jarvis.skills.project_architect import ProjectArchitectSkill
from jarvis.skills.code_generator import CodeGeneratorSkill
from jarvis.skills.github_automation import GitHubAutomationSkill
from jarvis.skills.ide_control import IDEControlSkill
from jarvis.skills.project_completion import ProjectCompletionSkill


def process_email_text(email_body: str):
    """
    Process email text manually.
    
    Args:
        email_body: The full text of your email
    """
    print("="*60)
    print("JARVIS Manual Email Processing")
    print("="*60)
    print()
    
    # Step 1: Extract requirements
    print("Step 1: Extracting requirements from email...")
    email_skill = EmailIntakeSkill()
    result = email_skill.execute(
        action="parse",
        email_body=email_body,
        output_path="jarvis_output/specs/manual_project_spec.json"
    )
    
    if not result.success:
        print(f"❌ Failed: {result.error_message}")
        return
    
    print(f"✅ Requirements extracted!")
    print(f"   Project: {result.result['spec']['project_name']}")
    print(f"   Stack: {', '.join(result.result['spec']['stack'])}")
    print(f"   Saved to: {result.result['saved_to']}")
    print()
    
    spec_path = result.result['saved_to']
    project_name = result.result['spec']['project_name']
    
    # Step 2: Generate architecture
    print("Step 2: Generating project architecture...")
    architect_skill = ProjectArchitectSkill()
    result = architect_skill.execute(
        spec_path=spec_path,
        output_dir=f"jarvis_output/architecture/{project_name}"
    )
    
    if not result.success:
        print(f"❌ Failed: {result.error_message}")
        return
    
    print(f"✅ Architecture generated!")
    print(f"   Output: {result.result['output_dir']}")
    print(f"   Files: {', '.join(result.result['files_created'])}")
    print()
    
    architecture_dir = result.result['output_dir']
    plan_path = os.path.join(architecture_dir, "PLAN.md")
    
    # Ask for approval
    print("="*60)
    print("ARCHITECTURE REVIEW")
    print("="*60)
    print(f"Architecture files created in: {architecture_dir}")
    print()
    print("Files created:")
    for file in result.result['files_created']:
        print(f"  - {file}")
    print()
    
    approval = input("Review the architecture and type 'yes' to continue with code generation: ").strip().lower()
    
    if approval != 'yes':
        print("❌ Code generation cancelled. Review the architecture and run again when ready.")
        return
    
    # Step 3: Generate code
    print()
    print("Step 3: Generating code with tests...")
    code_gen_skill = CodeGeneratorSkill()
    result = code_gen_skill.execute(
        action="iterate",
        plan_path=plan_path,
        output_dir=f"jarvis_output/generated_code/{project_name}",
        max_iterations=3
    )
    
    if not result.success:
        print(f"⚠️  Code generation had issues: {result.error_message}")
    else:
        print(f"✅ Code generated!")
        print(f"   Output: {result.result['output_dir']}")
        print(f"   Iterations: {result.result['iterations']}")
        print(f"   Tests passed: {result.result['test_passed']}")
    
    code_dir = result.result.get('output_dir', f"jarvis_output/generated_code/{project_name}")
    print()
    
    # Step 4: Open in VS Code
    print("Step 4: Opening project in VS Code...")
    ide_skill = IDEControlSkill()
    result = ide_skill.execute(
        action="open_vscode",
        project_path=code_dir
    )
    
    if result.success:
        print(f"✅ Opened in VS Code!")
    
    # Step 5: Install dependencies
    print()
    print("Step 5: Installing dependencies...")
    result = ide_skill.execute(
        action="install_deps",
        project_path=code_dir,
        package_manager="npm"
    )
    
    if result.success:
        print(f"✅ Dependencies installed!")
    
    # Summary
    print()
    print("="*60)
    print("PROJECT READY! 🎉")
    print("="*60)
    print()
    print(f"Project: {project_name}")
    print(f"Location: {code_dir}")
    print()
    print("Next steps:")
    print(f"  1. Review the code in VS Code")
    print(f"  2. Run tests: cd {code_dir} && npm test")
    print(f"  3. Start dev server: npm run dev")
    print(f"  4. Initialize git: git init")
    print(f"  5. Create GitHub repo and push")
    print()


def main():
    """Main entry point."""
    print()
    print("JARVIS Manual Email Processor")
    print("="*60)
    print()
    print("Paste your email content below.")
    print("Press Ctrl+Z (Windows) or Ctrl+D (Unix) and Enter when done.")
    print()
    print("Email content:")
    print("-"*60)
    
    # Read multi-line input
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    email_body = "\n".join(lines)
    
    if not email_body.strip():
        print()
        print("❌ No email content provided!")
        print()
        print("Usage:")
        print("  python process_email_manual.py")
        print()
        print("Then paste your email and press Ctrl+Z + Enter")
        return
    
    print()
    print("-"*60)
    print()
    
    # Process the email
    process_email_text(email_body)


if __name__ == "__main__":
    main()
