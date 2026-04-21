"""System Status Skill for JARVIS using psutil.

Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5, 13.6
"""

import time
from typing import Any, Dict, List
import psutil

from jarvis.skills.base import Skill, SkillResult


class SystemStatusSkill(Skill):
    """
    System status skill that reports CPU, RAM, disk usage and top processes.
    
    Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5, 13.6
    """
    
    def __init__(self):
        """Initialize the system status skill."""
        super().__init__()
        self._name = "system_status"
        self._description = "Report system health including CPU usage, RAM usage, disk usage, and top 5 processes by resource consumption."
        self._parameters = {
            "type": "object",
            "properties": {},
            "required": []  # No parameters required per requirement 13.1
        }
    
    def execute(self, **kwargs) -> SkillResult:
        """
        Execute system status check.
        
        Args:
            **kwargs: No parameters required
            
        Returns:
            SkillResult with system status information
            
        Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5, 13.6
        """
        start_time = time.time()
        
        # Validate parameters (should always pass since no params required)
        is_valid, error_msg = self.validate_parameters(**kwargs)
        if not is_valid:
            return SkillResult(
                success=False,
                result=None,
                error_message=error_msg,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        try:
            # Get CPU usage percentage (requirement 13.2)
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            cpu_info = {
                "usage_percent": cpu_percent,
                "core_count": cpu_count,
                "current_freq_mhz": cpu_freq.current if cpu_freq else None,
                "max_freq_mhz": cpu_freq.max if cpu_freq else None
            }
            
            # Get RAM usage in GB and percentage (requirement 13.3)
            memory = psutil.virtual_memory()
            ram_info = {
                "total_gb": round(memory.total / (1024 ** 3), 2),
                "used_gb": round(memory.used / (1024 ** 3), 2),
                "available_gb": round(memory.available / (1024 ** 3), 2),
                "usage_percent": memory.percent
            }
            
            # Get disk usage in GB and percentage (requirement 13.4)
            disk = psutil.disk_usage('/')
            disk_info = {
                "total_gb": round(disk.total / (1024 ** 3), 2),
                "used_gb": round(disk.used / (1024 ** 3), 2),
                "free_gb": round(disk.free / (1024 ** 3), 2),
                "usage_percent": disk.percent
            }
            
            # Get top 5 processes by resource consumption (requirement 13.5)
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cpu_percent': proc_info['cpu_percent'] or 0,
                        'memory_percent': proc_info['memory_percent'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Skip processes we can't access
                    pass
            
            # Sort by combined resource usage (CPU + memory)
            processes.sort(
                key=lambda p: p['cpu_percent'] + p['memory_percent'],
                reverse=True
            )
            
            # Get top 5 processes
            top_processes = []
            for proc in processes[:5]:
                top_processes.append({
                    "pid": proc['pid'],
                    "name": proc['name'],
                    "cpu_percent": round(proc['cpu_percent'], 2),
                    "memory_percent": round(proc['memory_percent'], 2)
                })
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return SkillResult(
                success=True,
                result={
                    "cpu": cpu_info,
                    "ram": ram_info,
                    "disk": disk_info,
                    "top_processes": top_processes
                },
                error_message=None,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            return SkillResult(
                success=False,
                result=None,
                error_message=f"Error retrieving system status: {str(e)}",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
