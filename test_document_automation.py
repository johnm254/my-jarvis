"""
Test document automation functionality
"""

from jarvis.skills.document_automation import DocumentAutomationSkill
import time

print("📄 Testing Document Automation\n")

doc_skill = DocumentAutomationSkill()

# Test 1: Open Word
print("1️⃣  Testing: Open Word")
result = doc_skill.execute(action="open_word")
if result.success:
    print(f"   ✅ {result.result}\n")
else:
    print(f"   ❌ Error: {result.error_message}\n")

time.sleep(3)

# Test 2: Create document with requirements
print("2️⃣  Testing: Complete workflow")
result = doc_skill.execute(
    action="complete_workflow",
    document_type="letter",
    requirements="Write a professional business letter to thank a client for their business",
    filename="test_business_letter",
    recipient_email="johnmwangi1729@gmail.com"
)

if result.success:
    print(f"   ✅ Workflow result: {result.result}\n")
else:
    print(f"   ❌ Workflow failed: {result.error_message}\n")

print("✅ Document automation test complete!")
print("   Check your Documents folder for the created file")
print("   Check your email for the notification\n")