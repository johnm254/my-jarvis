"""
Document Automation Skill - Create, format, and manage Word documents with email notifications
"""

import os
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from jarvis.skills.base import Skill, SkillResult
from jarvis.skills.email_notifier import EmailNotifierSkill

logger = logging.getLogger(__name__)


class DocumentAutomationSkill(Skill):
    """Create, format, and manage Word documents with automated email notifications."""
    
    def __init__(self):
        super().__init__()
        self._name = "document_automation"
        self._description = (
            "Create, format, and manage Word documents. Can open Word, write content "
            "based on requirements, format documents, save them, and send email "
            "notifications when complete."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": (
                        "Action to perform: 'create_document', 'open_word', "
                        "'write_content', 'format_document', 'save_document', "
                        "or 'complete_workflow' (does everything)"
                    ),
                },
                "document_type": {
                    "type": "string",
                    "description": "Type of document: letter, report, memo, proposal, etc.",
                },
                "requirements": {
                    "type": "string",
                    "description": "Content requirements and specifications for the document.",
                },
                "filename": {
                    "type": "string",
                    "description": "Name for the document file (without extension).",
                },
                "recipient_email": {
                    "type": "string",
                    "description": "Email address to notify when document is complete.",
                },
                "content": {
                    "type": "string",
                    "description": "Specific content to write in the document.",
                },
            },
            "required": ["action"],
        }
        
        # Initialize email notifier
        self.email_notifier = EmailNotifierSkill()
    
    def execute(self, **kwargs) -> SkillResult:
        """Execute document automation action."""
        start = time.time()
        action = kwargs.get("action")
        
        try:
            if action == "open_word":
                result = self._open_word(**kwargs)
            elif action == "create_document":
                result = self._create_document(**kwargs)
            elif action == "write_content":
                result = self._write_content(**kwargs)
            elif action == "format_document":
                result = self._format_document(**kwargs)
            elif action == "save_document":
                result = self._save_document(**kwargs)
            elif action == "complete_workflow":
                result = self._complete_workflow(**kwargs)
            else:
                return SkillResult(
                    success=False,
                    result=None,
                    error_message=f"Unknown action: {action}",
                    execution_time_ms=int((time.time() - start) * 1000)
                )
            
            return SkillResult(
                success=True,
                result=result,
                execution_time_ms=int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            logger.error(f"Document automation error: {e}")
            return SkillResult(
                success=False,
                result=None,
                error_message=str(e),
                execution_time_ms=int((time.time() - start) * 1000)
            )
    
    def _open_word(self, **kwargs):
        """Open Microsoft Word."""
        try:
            # Try different Word paths
            word_paths = [
                r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
                r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE",
                r"C:\Program Files (x86)\Microsoft Office\Office16\WINWORD.EXE",
                "winword",  # If in PATH
            ]
            
            word_opened = False
            for word_path in word_paths:
                try:
                    if word_path == "winword":
                        subprocess.Popen(word_path, shell=True)
                    else:
                        if os.path.exists(word_path):
                            subprocess.Popen(word_path)
                    word_opened = True
                    logger.info(f"Opened Word using: {word_path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to open Word with {word_path}: {e}")
                    continue
            
            if not word_opened:
                # Try opening any .docx file to launch Word
                try:
                    # Create a temporary document
                    temp_doc = Path.home() / "Desktop" / "temp_jarvis.docx"
                    temp_doc.touch()
                    os.startfile(str(temp_doc))
                    word_opened = True
                    logger.info("Opened Word by creating temporary document")
                except Exception as e:
                    logger.warning(f"Failed to open Word via file association: {e}")
            
            if word_opened:
                time.sleep(3)  # Wait for Word to load
                return {"opened": True, "application": "Microsoft Word"}
            else:
                return {"opened": False, "error": "Could not find or open Microsoft Word"}
                
        except Exception as e:
            return {"opened": False, "error": str(e)}
    
    def _create_document(self, **kwargs):
        """Create a new document."""
        try:
            import pyautogui
            pyautogui.FAILSAFE = False
            
            # Open Word first
            word_result = self._open_word(**kwargs)
            if not word_result.get("opened", False):
                return {"created": False, "error": "Could not open Word"}
            
            # Create new document (Ctrl+N)
            time.sleep(2)
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(2)
            
            return {"created": True, "document": "New document created"}
            
        except Exception as e:
            return {"created": False, "error": str(e)}
    
    def _write_content(self, **kwargs):
        """Write content to the document based on requirements."""
        try:
            import pyautogui
            pyautogui.FAILSAFE = False
            
            requirements = kwargs.get("requirements", "")
            content = kwargs.get("content", "")
            document_type = kwargs.get("document_type", "document")
            
            if not requirements and not content:
                return {"written": False, "error": "No requirements or content provided"}
            
            # Generate content based on requirements
            if requirements and not content:
                content = self._generate_content(requirements, document_type)
            
            # Type the content
            pyautogui.write(content, interval=0.01)
            
            return {
                "written": True,
                "content_length": len(content),
                "document_type": document_type
            }
            
        except Exception as e:
            return {"written": False, "error": str(e)}
    
    def _generate_content(self, requirements: str, document_type: str) -> str:
        """Generate document content based on requirements."""
        try:
            # Use the LLM to generate content
            from groq import Groq
            client = Groq(api_key=os.getenv("LLM_API_KEY"))
            
            prompt = f"""
Create a professional {document_type} based on these requirements:

{requirements}

Please write a complete, well-structured {document_type} that:
1. Follows proper formatting for a {document_type}
2. Is professional and appropriate
3. Includes all necessary sections
4. Is ready to use

Write only the document content, no explanations or meta-text.
"""
            
            response = client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return content
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            # Fallback content
            return f"""
{document_type.title()}

Date: {datetime.now().strftime('%B %d, %Y')}

Requirements: {requirements}

This document was created based on the provided requirements. Please review and modify as needed.

Best regards,
JARVIS Document Automation
"""
    
    def _format_document(self, **kwargs):
        """Apply formatting to the document."""
        try:
            import pyautogui
            pyautogui.FAILSAFE = False
            
            # Select all text
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.5)
            
            # Apply basic formatting
            # Set font to Calibri 11pt
            pyautogui.hotkey('ctrl', 'shift', 'f')  # Font dialog
            time.sleep(1)
            pyautogui.write('Calibri', interval=0.01)
            pyautogui.press('tab')
            pyautogui.write('11', interval=0.01)
            pyautogui.press('enter')
            time.sleep(1)
            
            # Set line spacing to 1.15
            pyautogui.hotkey('ctrl', '1')  # Single spacing first
            time.sleep(0.5)
            
            # Add some basic formatting
            pyautogui.press('home')  # Go to beginning
            pyautogui.hotkey('shift', 'end')  # Select first line (title)
            pyautogui.hotkey('ctrl', 'b')  # Bold
            pyautogui.press('end')  # Deselect
            
            return {"formatted": True, "formatting": "Applied professional formatting"}
            
        except Exception as e:
            return {"formatted": False, "error": str(e)}
    
    def _save_document(self, **kwargs):
        """Save the document."""
        try:
            import pyautogui
            pyautogui.FAILSAFE = False
            
            filename = kwargs.get("filename", f"JARVIS_Document_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Save document (Ctrl+S)
            pyautogui.hotkey('ctrl', 's')
            time.sleep(2)
            
            # Type filename
            pyautogui.write(filename, interval=0.01)
            time.sleep(1)
            
            # Press Enter to save
            pyautogui.press('enter')
            time.sleep(2)
            
            # Get the likely save path
            save_path = Path.home() / "Documents" / f"{filename}.docx"
            
            return {
                "saved": True,
                "filename": f"{filename}.docx",
                "path": str(save_path)
            }
            
        except Exception as e:
            return {"saved": False, "error": str(e)}
    
    def _complete_workflow(self, **kwargs):
        """Complete the entire document creation workflow."""
        try:
            results = {}
            
            # Step 1: Open Word
            logger.info("Step 1: Opening Microsoft Word...")
            word_result = self._open_word(**kwargs)
            results["word_opened"] = word_result
            
            if not word_result.get("opened", False):
                raise Exception("Could not open Microsoft Word")
            
            # Step 2: Create new document
            logger.info("Step 2: Creating new document...")
            create_result = self._create_document(**kwargs)
            results["document_created"] = create_result
            
            # Step 3: Write content
            logger.info("Step 3: Writing content...")
            write_result = self._write_content(**kwargs)
            results["content_written"] = write_result
            
            if not write_result.get("written", False):
                raise Exception("Could not write content to document")
            
            # Step 4: Format document
            logger.info("Step 4: Formatting document...")
            format_result = self._format_document(**kwargs)
            results["document_formatted"] = format_result
            
            # Step 5: Save document
            logger.info("Step 5: Saving document...")
            save_result = self._save_document(**kwargs)
            results["document_saved"] = save_result
            
            # Step 6: Send email notification
            recipient_email = kwargs.get("recipient_email")
            if recipient_email:
                logger.info("Step 6: Sending email notification...")
                email_result = self._send_completion_email(recipient_email, save_result, **kwargs)
                results["email_sent"] = email_result
            
            return {
                "workflow_complete": True,
                "steps_completed": 6 if recipient_email else 5,
                "results": results,
                "document_path": save_result.get("path", "Unknown"),
                "filename": save_result.get("filename", "Unknown")
            }
            
        except Exception as e:
            return {"workflow_complete": False, "error": str(e), "results": results}
    
    def _send_completion_email(self, recipient_email: str, save_result: dict, **kwargs):
        """Send email notification when document is complete."""
        try:
            document_type = kwargs.get("document_type", "document")
            filename = save_result.get("filename", "Unknown")
            path = save_result.get("path", "Unknown")
            
            subject = f"JARVIS: {document_type.title()} Complete - {filename}"
            
            body = f"""
Hello!

JARVIS has successfully completed your {document_type} automation task.

Document Details:
- Type: {document_type.title()}
- Filename: {filename}
- Location: {path}
- Created: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

The document has been:
✅ Created and formatted
✅ Content written based on your requirements
✅ Professionally formatted
✅ Saved to your Documents folder

You can now open and review the document. If you need any modifications, just ask JARVIS!

Best regards,
JARVIS Document Automation System
"""
            
            email_result = self.email_notifier.execute(
                to=recipient_email,
                subject=subject,
                body=body
            )
            
            return {
                "email_sent": email_result.success,
                "recipient": recipient_email,
                "error": email_result.error_message if not email_result.success else None
            }
            
        except Exception as e:
            return {"email_sent": False, "error": str(e)}