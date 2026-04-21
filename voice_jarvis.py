"""
Voice-Controlled JARVIS

Talk to JARVIS and get things done:
- "Hey Jarvis, diagnose my computer"
- "Hey Jarvis, clean up my system"
- "Hey Jarvis, send me a diagnostic report"
- "Hey Jarvis, free up 50 gigabytes"
- "Hey Jarvis, optimize my computer"
"""

import os
import json
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

from jarvis.skills.computer_diagnostics import ComputerDiagnosticsSkill
from jarvis.skills.system_optimizer import SystemOptimizerSkill
from jarvis.skills.email_notifier import EmailNotifierSkill


class VoiceJARVIS:
    """Voice-controlled JARVIS assistant."""
    
    def __init__(self):
        """Initialize voice JARVIS."""
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Text-to-speech
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 175)  # Speed
        self.engine.setProperty('volume', 0.9)  # Volume
        
        # Try to set a better voice
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "david" in voice.name.lower() or "mark" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Skills
        self.diagnostics_skill = ComputerDiagnosticsSkill()
        self.optimizer_skill = SystemOptimizerSkill()
        self.email_skill = EmailNotifierSkill()
        
        # State
        self.last_diagnostic = None
        self.listening = True
        
        print("🤖 Voice JARVIS initialized")
        print("   Microphone ready")
        print("   Text-to-speech ready")
        print()
    
    def speak(self, text: str):
        """Speak text out loud."""
        print(f"🗣️  JARVIS: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self) -> str:
        """Listen for voice command."""
        with self.microphone as source:
            print("🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("🔄 Processing...")
                
                # Use Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                print(f"👤 You: {text}")
                return text.lower()
                
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't catch that. Could you repeat?")
                return ""
            except sr.RequestError:
                self.speak("Sorry, my speech recognition service is unavailable.")
                return ""
    
    def handle_command(self, command: str):
        """Handle voice command."""
        
        # Diagnose computer
        if any(word in command for word in ["diagnose", "diagnostic", "check computer", "scan computer", "health check"]):
            self.speak("Running comprehensive system diagnostics. This will take a moment.")
            
            result = self.diagnostics_skill.execute(scan_type="full")
            
            if result.success:
                self.last_diagnostic = result.result
                
                # Generate summary
                data = result.result
                sys_info = data.get("system", {})
                mem_info = data.get("memory", {})
                disk_info = data.get("disk", {})
                
                # Calculate health score
                health_score = 100
                issues = []
                
                # Check disk
                for disk in disk_info.get("disks", []):
                    if disk['usage_percent'] > 90:
                        health_score -= 15
                        issues.append(f"Disk {disk['drive']} is {disk['usage_percent']} percent full")
                    elif disk['usage_percent'] > 75:
                        health_score -= 5
                        issues.append(f"Disk {disk['drive']} is getting full at {disk['usage_percent']} percent")
                
                # Check security
                sec_info = data.get("security", {})
                if sec_info.get("antivirus") == "disabled":
                    health_score -= 20
                    issues.append("Antivirus is disabled")
                
                # Speak results
                self.speak(f"Diagnostic complete. Your computer health score is {health_score} out of 100.")
                
                if health_score >= 90:
                    self.speak("Your system is in excellent condition.")
                elif health_score >= 75:
                    self.speak("Your system is in good condition.")
                else:
                    self.speak("Your system needs attention.")
                
                if issues:
                    self.speak(f"I found {len(issues)} issues.")
                    for issue in issues[:3]:  # Top 3 issues
                        self.speak(issue)
                else:
                    self.speak("No issues detected.")
                
                self.speak("Would you like me to send you a detailed report via email?")
            else:
                self.speak(f"Diagnostic failed. {result.error_message}")
        
        # Send report
        elif any(word in command for word in ["send report", "email report", "send diagnostic", "email me"]):
            if self.last_diagnostic:
                self.speak("Generating and sending diagnostic report.")
                
                # Generate HTML report
                report_html = self._generate_html_report(self.last_diagnostic)
                
                # Send email
                email = os.getenv("NOTIFICATION_EMAIL")
                result = self.email_skill.execute(
                    to=email,
                    subject=f"JARVIS Diagnostic Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    body=report_html
                )
                
                if result.success:
                    self.speak(f"Diagnostic report sent to {email}")
                else:
                    self.speak("Failed to send email. Please check your email configuration.")
            else:
                self.speak("No diagnostic data available. Please run a diagnostic first.")
        
        # Clean up / Optimize
        elif any(word in command for word in ["clean", "optimize", "free space", "clean up", "speed up"]):
            # Extract target GB if mentioned
            target_gb = 50
            if "gigabyte" in command or "gb" in command:
                words = command.split()
                for i, word in enumerate(words):
                    if word.isdigit():
                        target_gb = int(word)
                        break
            
            self.speak(f"Starting system optimization. I'll try to free up {target_gb} gigabytes.")
            
            result = self.optimizer_skill.execute(action="free_space", target_gb=target_gb)
            
            if result.success:
                data = result.result
                freed = data.get("total_freed_gb", 0)
                
                self.speak(f"Optimization complete. I freed up {freed} gigabytes of disk space.")
                
                actions = data.get("actions", [])
                self.speak(f"I performed {len(actions)} cleanup actions:")
                for action in actions[:3]:
                    self.speak(f"{action['action']}: {action['freed_gb']} gigabytes")
                
                if data.get("target_met"):
                    self.speak("Target achieved!")
                else:
                    self.speak(f"I freed up {freed} gigabytes, but the target was {target_gb}. You may need to manually delete large files.")
            else:
                self.speak(f"Optimization failed. {result.error_message}")
        
        # Enable antivirus
        elif any(word in command for word in ["enable antivirus", "turn on antivirus", "activate defender"]):
            self.speak("Enabling Windows Defender antivirus.")
            
            result = os.system('powershell -command "Set-MpPreference -DisableRealtimeMonitoring $false"')
            
            if result == 0:
                self.speak("Windows Defender is now enabled and protecting your computer.")
            else:
                self.speak("Failed to enable antivirus. You may need to do this manually in Windows Security.")
        
        # Help
        elif any(word in command for word in ["help", "what can you do", "commands"]):
            self.speak("I can help you with:")
            self.speak("Diagnose my computer - Run a full system diagnostic")
            self.speak("Send me a report - Email the diagnostic report")
            self.speak("Clean up my system - Free up disk space")
            self.speak("Optimize my computer - Run all optimizations")
            self.speak("Enable antivirus - Turn on Windows Defender")
            self.speak("Stop listening - Exit voice mode")
        
        # Exit
        elif any(word in command for word in ["stop", "exit", "quit", "goodbye", "bye"]):
            self.speak("Goodbye! I'll be here if you need me.")
            self.listening = False
        
        # Unknown command
        else:
            self.speak("I'm not sure how to help with that. Say 'help' to hear what I can do.")
    
    def _generate_html_report(self, data: dict) -> str:
        """Generate HTML diagnostic report."""
        sys_info = data.get("system", {})
        cpu_info = data.get("cpu", {})
        mem_info = data.get("memory", {})
        disk_info = data.get("disk", {})
        net_info = data.get("network", {})
        sec_info = data.get("security", {})
        
        html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2196F3; }}
        h2 {{ color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 5px; }}
        .section {{ margin: 20px 0; }}
        .good {{ color: green; }}
        .warning {{ color: orange; }}
        .critical {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>🤖 JARVIS Diagnostic Report</h1>
    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="section">
        <h2>💻 System Information</h2>
        <table>
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>Operating System</td><td>{sys_info.get('os')} {sys_info.get('os_release')}</td></tr>
            <tr><td>Architecture</td><td>{sys_info.get('architecture')}</td></tr>
            <tr><td>Hostname</td><td>{sys_info.get('hostname')}</td></tr>
            <tr><td>CPU Cores</td><td>{cpu_info.get('cores')}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>💾 Memory</h2>
        <p>Total: {mem_info.get('total_gb', 'N/A')} GB</p>
        <p>Used: {mem_info.get('used_gb', 'N/A')} GB ({mem_info.get('usage_percent', 'N/A')}%)</p>
        <p>Free: {mem_info.get('free_gb', 'N/A')} GB</p>
    </div>
    
    <div class="section">
        <h2>💿 Disk Space</h2>
        <table>
            <tr><th>Drive</th><th>Total</th><th>Used</th><th>Free</th><th>Usage</th></tr>
"""
        
        for disk in disk_info.get("disks", []):
            usage_class = "critical" if disk['usage_percent'] > 90 else "warning" if disk['usage_percent'] > 75 else "good"
            html += f"""
            <tr>
                <td>{disk['drive']}</td>
                <td>{disk['total_gb']} GB</td>
                <td>{disk['used_gb']} GB</td>
                <td>{disk['free_gb']} GB</td>
                <td class="{usage_class}">{disk['usage_percent']}%</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>🔒 Security</h2>
        <p>Antivirus: <span class="{}">{}</span></p>
        <p>Firewall: <span class="{}">{}</span></p>
    </div>
    
    <div class="section">
        <h2>🌐 Network</h2>
        <p>Internet: {}</p>
        <p>DNS: {}</p>
    </div>
    
    <div class="section">
        <h2>📊 Recommendations</h2>
        <ul>
""".format(
            "critical" if sec_info.get("antivirus") == "disabled" else "good",
            sec_info.get("antivirus", "unknown"),
            "critical" if sec_info.get("firewall") == "disabled" else "good",
            sec_info.get("firewall", "unknown"),
            "✅ Connected" if net_info.get("internet_connected") else "❌ Disconnected",
            "✅ Working" if net_info.get("dns_working") else "❌ Not Working"
        )
        
        # Add recommendations
        for disk in disk_info.get("disks", []):
            if disk['usage_percent'] > 75:
                html += f"<li>Free up space on drive {disk['drive']} (currently {disk['usage_percent']}% full)</li>"
        
        if sec_info.get("antivirus") == "disabled":
            html += "<li>Enable Windows Defender antivirus</li>"
        
        html += """
        </ul>
    </div>
</body>
</html>
"""
        
        return html
    
    def run(self):
        """Run voice JARVIS."""
        self.speak("Hello! I'm JARVIS, your voice-controlled assistant.")
        self.speak("Say 'Hey Jarvis' followed by your command, or say 'help' to hear what I can do.")
        
        while self.listening:
            command = self.listen()
            
            if command:
                # Check for wake word
                if "jarvis" in command or "hey jarvis" in command:
                    # Remove wake word
                    command = command.replace("hey jarvis", "").replace("jarvis", "").strip()
                    
                    if command:
                        self.handle_command(command)
                elif command and not any(word in command for word in ["hey", "hi", "hello"]):
                    # If no wake word but has content, process anyway
                    self.handle_command(command)


def main():
    """Main entry point."""
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║              Voice-Controlled JARVIS                     ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    try:
        jarvis = VoiceJARVIS()
        jarvis.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  - pip install SpeechRecognition")
        print("  - pip install pyttsx3")
        print("  - pip install pyaudio")
        print("  - A working microphone")


if __name__ == "__main__":
    main()
