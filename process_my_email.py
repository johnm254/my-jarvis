"""
Quick Email Processor - Just paste your email here!
"""

import os
from dotenv import load_dotenv
load_dotenv()

from jarvis.skills.email_intake import EmailIntakeSkill
from jarvis.skills.project_architect import ProjectArchitectSkill
from jarvis.skills.code_generator import CodeGeneratorSkill
from jarvis.skills.ide_control import IDEControlSkill

# ============================================================
# PASTE YOUR EMAIL CONTENT BELOW (between the triple quotes)
# ============================================================

EMAIL_CONTENT = """
To: johnmwangi1729+jarvis@gmail.com
Subject: [JARVIS] Build My Project

Hi JARVIS,

Project Name: TaskMaster Pro
Stack: React, TypeScript, Node.js, PostgreSQL
Deadline: 2 weeks

Features:
- User authentication
- Task management
- Dashboard with analytics
- REST API

Thanks!
"""

# ============================================================
# Don't edit below this line
# ============================================================

def main():
    if "PASTE YOUR EMAIL HERE" in EMAIL_CONTENT:
        print("❌ Please paste your actual email content in the EMAIL_CONTENT variable above!")
        print()
        print("Open this file (process_my_email.py) and replace the EMAIL_CONTENT text.")
        return
    
    print("🤖 Processing your email...")
    print()
    
    # Step 1: Extract requirements
    print("📧 Step 1: Extracting requirements...")
    email_skill = EmailIntakeSkill()
    result = email_skill.execute(
        action="parse",
        email_body=EMAIL_CONTENT,
        output_path="jarvis_output/specs/my_project_spec.json"
    )
    
    if not result.success:
        print(f"❌ Failed: {result.error_message}")
        return
    
    spec = result.result['spec']
    print(f"✅ Requirements extracted!")
    print(f"   Project: {spec['project_name']}")
    print(f"   Stack: {', '.join(spec['stack'])}")
    print(f"   Features: {len(spec['features'])} features")
    print()
    
    # Step 2: Generate architecture
    print("🏗️  Step 2: Generating architecture...")
    architect_skill = ProjectArchitectSkill()
    result = architect_skill.execute(
        spec_path=result.result['saved_to'],
        output_dir=f"jarvis_output/architecture/{spec['project_name']}"
    )
    
    if not result.success:
        print(f"❌ Failed: {result.error_message}")
        return
    
    print(f"✅ Architecture generated!")
    print(f"   Files: {', '.join(result.result['files_created'])}")
    print()
    
    # Step 3: Generate code
    print("💻 Step 3: Generating code (this may take a minute)...")
    code_gen_skill = CodeGeneratorSkill()
    plan_path = os.path.join(result.result['output_dir'], "PLAN.md")
    
    result = code_gen_skill.execute(
        action="iterate",
        plan_path=plan_path,
        output_dir=f"jarvis_output/generated_code/{spec['project_name']}",
        max_iterations=3
    )
    
    if result.success:
        print(f"✅ Code generated!")
        print(f"   Tests passed: {result.result.get('test_passed', False)}")
    else:
        print(f"⚠️  Code generation completed with warnings")
    
    code_dir = result.result.get('output_dir', f"jarvis_output/generated_code/{spec['project_name']}")
    print()
    
    # Step 4: Open in VS Code
    print("🖥️  Step 4: Opening in VS Code...")
    ide_skill = IDEControlSkill()
    ide_skill.execute(action="open_vscode", project_path=code_dir)
    print(f"✅ Opened in VS Code!")
    print()
    
    # Step 5: Install dependencies
    print("📦 Step 5: Installing dependencies...")
    result = ide_skill.execute(
        action="install_deps",
        project_path=code_dir,
        package_manager="npm"
    )
    
    if result.success:
        print(f"✅ Dependencies installed!")
    print()
    
    # Done!
    print("="*60)
    print("🎉 PROJECT READY!")
    print("="*60)
    print()
    print(f"📁 Location: {code_dir}")
    print()
    print("Next steps:")
    print(f"  1. Review code in VS Code (already open)")
    print(f"  2. cd {code_dir}")
    print(f"  3. npm test")
    print(f"  4. npm run dev")
    print()


if __name__ == "__main__":
    main()
