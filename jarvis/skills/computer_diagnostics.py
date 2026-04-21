"""Computer Diagnostics Skill

Comprehensive system diagnostics for your entire computer:
- Hardware info (CPU, GPU, RAM, Disk)
- Software info (OS, drivers, installed programs)
- Network diagnostics
- Performance monitoring
- Health checks
- Security scan
- Disk health
- Temperature monitoring
"""

import os
import platform
import subprocess
import time
import logging
from typing import Dict, Any, Optional
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class ComputerDiagnosticsSkill(Skill):
    """
    Comprehensive computer diagnostics skill.
    
    Provides detailed information about:
    - System hardware
    - Operating system
    - Network status
    - Disk health
    - Performance metrics
    - Security status
    - Installed software
    """
    
    def __init__(self):
        super().__init__()
        self._name = "computer_diagnostics"
        self._description = (
            "Comprehensive computer diagnostics: hardware, software, network, "
            "performance, security, disk health, and temperature monitoring"
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "scan_type": {
                    "type": "string",
                    "description": "Type of diagnostic scan",
                    "enum": [
                        "full",        # Complete system scan
                        "quick",       # Quick health check
                        "hardware",    # Hardware info only
                        "software",    # Software info only
                        "network",     # Network diagnostics
                        "performance", # Performance metrics
                        "security",    # Security scan
                        "disk",        # Disk health
                        "temperature"  # Temperature monitoring
                    ]
                }
            },
            "required": ["scan_type"]
        }
    
    def _run_command(self, cmd: str) -> Dict[str, Any]:
        """Run command and return output."""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            return {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "success": result.returncode == 0
            }
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "success": False}
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get basic system information."""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        }
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information."""
        info = {"cores": os.cpu_count()}
        
        # Windows-specific
        if platform.system() == "Windows":
            result = self._run_command("wmic cpu get name,numberofcores,maxclockspeed")
            if result["success"]:
                info["details"] = result["stdout"]
        
        return info
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        info = {}
        
        if platform.system() == "Windows":
            # Total memory
            result = self._run_command("wmic computersystem get totalphysicalmemory")
            if result["success"]:
                try:
                    lines = result["stdout"].split('\n')
                    if len(lines) > 1:
                        total_bytes = int(lines[1].strip())
                        total_gb = total_bytes / (1024**3)
                        info["total_gb"] = round(total_gb, 2)
                except:
                    pass
            
            # Available memory
            result = self._run_command("wmic OS get FreePhysicalMemory")
            if result["success"]:
                try:
                    lines = result["stdout"].split('\n')
                    if len(lines) > 1:
                        free_kb = int(lines[1].strip())
                        free_gb = free_kb / (1024**2)
                        info["free_gb"] = round(free_gb, 2)
                        if "total_gb" in info:
                            info["used_gb"] = round(info["total_gb"] - free_gb, 2)
                            info["usage_percent"] = round((info["used_gb"] / info["total_gb"]) * 100, 1)
                except:
                    pass
        
        return info
    
    def _get_disk_info(self) -> Dict[str, Any]:
        """Get disk information."""
        disks = []
        
        if platform.system() == "Windows":
            result = self._run_command("wmic logicaldisk get caption,size,freespace,filesystem")
            if result["success"]:
                lines = result["stdout"].split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 4:
                        try:
                            drive = parts[0]
                            filesystem = parts[1]
                            free_bytes = int(parts[2])
                            total_bytes = int(parts[3])
                            
                            free_gb = free_bytes / (1024**3)
                            total_gb = total_bytes / (1024**3)
                            used_gb = total_gb - free_gb
                            usage_percent = (used_gb / total_gb) * 100
                            
                            disks.append({
                                "drive": drive,
                                "filesystem": filesystem,
                                "total_gb": round(total_gb, 2),
                                "used_gb": round(used_gb, 2),
                                "free_gb": round(free_gb, 2),
                                "usage_percent": round(usage_percent, 1)
                            })
                        except:
                            pass
        
        return {"disks": disks}
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information."""
        info = {}
        
        if platform.system() == "Windows":
            result = self._run_command("wmic path win32_VideoController get name,adapterram")
            if result["success"]:
                info["details"] = result["stdout"]
        
        # Check for NVIDIA GPU
        result = self._run_command("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader")
        if result["success"] and result["stdout"]:
            info["nvidia"] = result["stdout"]
        
        return info
    
    def _get_network_info(self) -> Dict[str, Any]:
        """Get network information."""
        info = {}
        
        # Network adapters
        if platform.system() == "Windows":
            result = self._run_command("ipconfig /all")
            if result["success"]:
                info["adapters"] = result["stdout"][:500]  # Truncate
        
        # Internet connectivity
        result = self._run_command("ping -n 1 8.8.8.8")
        info["internet_connected"] = result["success"]
        
        # DNS test
        result = self._run_command("nslookup google.com")
        info["dns_working"] = result["success"]
        
        return info
    
    def _get_installed_software(self) -> Dict[str, Any]:
        """Get list of installed software."""
        software = []
        
        if platform.system() == "Windows":
            result = self._run_command("wmic product get name,version")
            if result["success"]:
                lines = result["stdout"].split('\n')[1:11]  # First 10
                software = [line.strip() for line in lines if line.strip()]
        
        return {"installed": software, "count": len(software)}
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        metrics = {}
        
        if platform.system() == "Windows":
            # CPU usage
            result = self._run_command("wmic cpu get loadpercentage")
            if result["success"]:
                try:
                    lines = result["stdout"].split('\n')
                    if len(lines) > 1:
                        metrics["cpu_usage_percent"] = int(lines[1].strip())
                except:
                    pass
            
            # Process count
            result = self._run_command("tasklist | find /c /v \"\"")
            if result["success"]:
                try:
                    metrics["process_count"] = int(result["stdout"].strip())
                except:
                    pass
        
        return metrics
    
    def _get_security_status(self) -> Dict[str, Any]:
        """Get security status."""
        status = {}
        
        if platform.system() == "Windows":
            # Windows Defender status
            result = self._run_command("powershell Get-MpComputerStatus | Select-String 'AntivirusEnabled'")
            if result["success"]:
                status["antivirus"] = "enabled" if "True" in result["stdout"] else "disabled"
            
            # Firewall status
            result = self._run_command("netsh advfirewall show allprofiles state")
            if result["success"]:
                status["firewall"] = "enabled" if "ON" in result["stdout"] else "disabled"
        
        return status
    
    def _get_temperature_info(self) -> Dict[str, Any]:
        """Get temperature information (if available)."""
        info = {"note": "Temperature monitoring requires additional tools"}
        
        # Try to get CPU temperature (requires external tools)
        # This is a placeholder - actual implementation would need tools like OpenHardwareMonitor
        
        return info
    
    def _quick_scan(self) -> Dict[str, Any]:
        """Quick health check."""
        return {
            "system": self._get_system_info(),
            "cpu_cores": os.cpu_count(),
            "memory": self._get_memory_info(),
            "disk": self._get_disk_info(),
            "network": {
                "internet": self._get_network_info().get("internet_connected", False)
            }
        }
    
    def _full_scan(self) -> Dict[str, Any]:
        """Complete system scan."""
        return {
            "system": self._get_system_info(),
            "cpu": self._get_cpu_info(),
            "memory": self._get_memory_info(),
            "disk": self._get_disk_info(),
            "gpu": self._get_gpu_info(),
            "network": self._get_network_info(),
            "software": self._get_installed_software(),
            "performance": self._get_performance_metrics(),
            "security": self._get_security_status(),
            "temperature": self._get_temperature_info()
        }
    
    def execute(self, **kwargs) -> SkillResult:
        start = time.time()
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(**kwargs)
        if not is_valid:
            return SkillResult(
                success=False,
                result=None,
                error_message=error_msg,
                execution_time_ms=int((time.time() - start) * 1000)
            )
        
        scan_type = kwargs.get("scan_type", "quick")
        
        try:
            if scan_type == "full":
                result = self._full_scan()
            elif scan_type == "quick":
                result = self._quick_scan()
            elif scan_type == "hardware":
                result = {
                    "system": self._get_system_info(),
                    "cpu": self._get_cpu_info(),
                    "memory": self._get_memory_info(),
                    "gpu": self._get_gpu_info()
                }
            elif scan_type == "software":
                result = {
                    "system": self._get_system_info(),
                    "installed": self._get_installed_software()
                }
            elif scan_type == "network":
                result = self._get_network_info()
            elif scan_type == "performance":
                result = self._get_performance_metrics()
            elif scan_type == "security":
                result = self._get_security_status()
            elif scan_type == "disk":
                result = self._get_disk_info()
            elif scan_type == "temperature":
                result = self._get_temperature_info()
            else:
                return SkillResult(
                    success=False,
                    result=None,
                    error_message=f"Unknown scan type: {scan_type}",
                    execution_time_ms=int((time.time() - start) * 1000)
                )
            
            return SkillResult(
                success=True,
                result=result,
                error_message=None,
                execution_time_ms=int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            logger.error(f"Error during diagnostics: {e}")
            return SkillResult(
                success=False,
                result=None,
                error_message=str(e),
                execution_time_ms=int((time.time() - start) * 1000)
            )
