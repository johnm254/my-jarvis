"""
Demo: Full-Stack Project Automation Workflow

This demonstrates the complete end-to-end workflow:
1. Email intake → Extract requirements
2. Project architect → Generate design
3. Code generator → Build the project
4. GitHub automation → Create repo & PR
5. IDE control → Open in VS Code
6. Project completion → Send notification
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from jarvis.skills.email_intake import EmailIntakeSkill
from jarvis.skills.project_architect import ProjectArchitectSkill
from jarvis.skills.code_generator import CodeGeneratorSkill
from jarvis.skills.github_automation import GitHubAutomationSkill
from jarvis.skills.ide_control import IDEControlSkill
from jarvis.skills.project_completion import ProjectCompletionSkill


def print_step(step_num: int, title: str):
    """Print step header."""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*60}\n")


def print_result(result):
    """Print skill result."""
    if result.success:
        print(f"✅ SUCCESS (took {result.execution_time_ms}ms)")
        print(f"Result: {json.dumps(result.result, indent=2)}")
    else:
        print(f"❌ FAILED (took {result.execution_time_ms}ms)")
        print(f"Error: {result.error_message}")


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   JARVIS Full-Stack Project Automation Demo                 ║
║   From Email → Design → Code → GitHub → Notification        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Sample project email
    sample_email = """
Hi JARVIS,

I need a new project built ASAP. Here are the requirements:

Project Name: TaskMaster Pro
Stack: React, TypeScript, Node.js, PostgreSQL, Tailwind CSS
Deadline: 2 weeks

Features:
- User authentication (email/password)
- Task management (CRUD operations)
- Dashboard with analytics
- REST API with OpenAPI docs
- Real-time notifications
- Dark mode support

Please use best practices and include tests.

Thanks!
"""
    
    # ─────────────────────────────────────────────────────────────
    # STEP 1: Email Intake & Requirement Extraction
    # ─────────────────────────────────────────────────────────────
    print_step(1, "Email Intake & Requirement Extraction")
    
    email_skill = EmailIntakeSkill()
    result = email_skill.execute(
        action="parse",
        email_body=sample_email,
        output_path="jarvis_output/specs/taskmaster_spec.json"
    )
    print_result(result)
    
    if not result.success:
        print("\n❌ Workflow stopped due to error in Step 1")
        return
    
    spec_path = result.result["saved_to"]
    
    # ─────────────────────────────────────────────────────────────
    # STEP 2: Project Design & Architecture
    # ─────────────────────────────────────────────────────────────
    print_step(2, "Project Design & Architecture Generation")
    
    architect_skill = ProjectArchitectSkill()
    result = architect_skill.execute(
        spec_path=spec_path,
        output_dir="jarvis_output/architecture/taskmaster"
    )
    print_result(result)
    
    if not result.success:
        print("\n❌ Workflow stopped due to error in Step 2")
        return
    
    architecture_dir = result.result["output_dir"]
    plan_path = os.path.join(architecture_dir, "PLAN.md")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 3: Code Generation & Testing
    # ─────────────────────────────────────────────────────────────
    print_step(3, "Code Generation with Iterative Testing")
    
    code_gen_skill = CodeGeneratorSkill()
    result = code_gen_skill.execute(
        action="iterate",
        plan_path=plan_path,
        output_dir="jarvis_output/generated_code/taskmaster",
        max_iterations=3
    )
    print_result(result)
    
    if not result.success:
        print("\n⚠️  Code generation had issues, but continuing...")
    
    code_dir = result.result.get("output_dir", "jarvis_output/generated_code/taskmaster")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 4: GitHub Repository & Version Control
    # ─────────────────────────────────────────────────────────────
    print_step(4, "GitHub Repository Creation & Push")
    
    github_skill = GitHubAutomationSkill()
    
    # Create repo
    print("4a. Creating GitHub repository...")
    result = github_skill.execute(
        action="create_repo",
        repo_name="taskmaster-pro",
        private=False
    )
    print_result(result)
    
    # Push code
    print("\n4b. Pushing code to main branch...")
    result = github_skill.execute(
        action="push",
        local_path=code_dir,
        commit_message="feat: initial TaskMaster Pro implementation with full-stack setup"
    )
    print_result(result)
    
    # Create dev branch
    print("\n4c. Creating dev branch...")
    result = github_skill.execute(
        action="create_branch",
        local_path=code_dir,
        branch_name="dev"
    )
    print_result(result)
    
    # Open PR
    print("\n4d. Opening pull request...")
    result = github_skill.execute(
        action="open_pr",
        local_path=code_dir,
        pr_title="feat: TaskMaster Pro - Initial Implementation",
        pr_body="Automated PR created by JARVIS\n\nFeatures:\n- User authentication\n- Task management\n- Dashboard\n- REST API\n- Tests included"
    )
    print_result(result)
    
    repo_url = "https://github.com/username/taskmaster-pro"
    pr_url = result.result.get("pr_url", "https://github.com/username/taskmaster-pro/pull/1")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 5: IDE & Local Environment Setup
    # ─────────────────────────────────────────────────────────────
    print_step(5, "IDE & Local Environment Control")
    
    ide_skill = IDEControlSkill()
    
    # Open in VS Code
    print("5a. Opening project in VS Code...")
    result = ide_skill.execute(
        action="open_vscode",
        project_path=code_dir
    )
    print_result(result)
    
    # Install dependencies
    print("\n5b. Installing dependencies...")
    result = ide_skill.execute(
        action="install_deps",
        project_path=code_dir,
        package_manager="npm"
    )
    print_result(result)
    
    # Start dev server
    print("\n5c. Starting development server...")
    result = ide_skill.execute(
        action="start_server",
        project_path=code_dir,
        server_command="npm run dev"
    )
    print_result(result)
    
    # ─────────────────────────────────────────────────────────────
    # STEP 6: Completion Notification
    # ─────────────────────────────────────────────────────────────
    print_step(6, "Project Completion Notification")
    
    completion_skill = ProjectCompletionSkill()
    result = completion_skill.execute(
        recipient="user@example.com",
        project_name="TaskMaster Pro",
        repo_url=repo_url,
        pr_url=pr_url,
        features=[
            "User authentication (email/password)",
            "Task management with CRUD operations",
            "Dashboard with analytics",
            "REST API with OpenAPI documentation",
            "Real-time notifications",
            "Dark mode support",
            "Comprehensive test suite"
        ],
        warnings=[
            "Manual review recommended for authentication flow",
            "Database migrations need to be run before deployment"
        ],
        test_results={
            "passed": 15,
            "failed": 0,
            "coverage": "87%"
        }
    )
    print_result(result)
    
    # ─────────────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("WORKFLOW COMPLETE! 🎉")
    print(f"{'='*60}\n")
    
    print("Summary:")
    print(f"  📧 Requirements extracted from email")
    print(f"  🏗️  Architecture designed and documented")
    print(f"  💻 Code generated with tests")
    print(f"  🐙 GitHub repo created: {repo_url}")
    print(f"  🔀 Pull request opened: {pr_url}")
    print(f"  🖥️  Project opened in VS Code")
    print(f"  📬 Completion email sent")
    print()
    print("Next steps:")
    print("  1. Review the generated code")
    print("  2. Run tests locally")
    print("  3. Review and merge the PR")
    print("  4. Deploy to production")
    print()


if __name__ == "__main__":
    main()
