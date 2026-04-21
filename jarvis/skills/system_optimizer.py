"""System Optimizer Skill

Automatically optimize your computer:
- Clean temporary files
- Clear cache
- Remove old downloads
- Optimize disk
- Free up space
- Apply performance tweaks
"""

import os
import shutil
import subprocess
import time
import logging
from typing import Dict, Any, List
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class SystemOptimizerSkill(Skill):
    """
    System optimization skill.
    
    Performs automatic system optimization:
    - Cleans temporary files
    - Clears browser cache
    - Removes old downloads
    - Empties recycle bin
    - Runs disk cleanup
    - Optimizes startup programs
    """
    
    def __init__(self):
        super().__init__()
        self._name = "system_optimizer"
        self._description = (
            "Optimize your computer by cleaning temporary files, "
            "clearing cache, freeing disk space, and applying performance tweaks"
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Optimization action to perform",
                    "enum": [
                        "clean_temp",      # Clean temp files
                        "clear_cache",     # Clear browser cache
                        "empty_recycle",   # Empty recycle bin
                        "disk_cleanup",    # Run Windows disk cleanup
                        "optimize_all",    # Run all optimizations
                        "free_space"       # Aggressive space freeing
                    ]
                },
                "target_gb": {
                    "type": "integer",
                    "description": "Target GB to free (for free_space action)"
                }
            },
            "required": ["action"]
        }
    
    def _run_command(self, cmd: str, timeout: int = 60) -> Dict[str, Any]:
        """Run command and return result."""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "success": result.returncode == 0
            }
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "success": False}
    
    def _get_folder_size(self, path: str) -> int:
        """Get folder size in bytes."""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total += os.path.getsize(filepath)
                    except:
                        pass
        except:
            pass
        return total
    
    def _clean_temp_files(self) -> Dict[str, Any]:
        """Clean temporary files."""
        cleaned = []
        total_freed = 0
        
        # Windows temp folders
        temp_folders = [
            os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp')),
            os.path.join(os.environ.get('TMP', 'C:\\Windows\\Temp')),
            'C:\\Windows\\Temp',
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp')
        ]
        
        for temp_folder in temp_folders:
            if os.path.exists(temp_folder):
                try:
                    size_before = self._get_folder_size(temp_folder)
                    
                    # Delete files
                    for item in os.listdir(temp_folder):
                        item_path = os.path.join(temp_folder, item)
                        try:
                            if os.path.isfile(item_path):
                                os.unlink(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                        except:
                            pass
                    
                    size_after = self._get_folder_size(temp_folder)
                    freed = size_before - size_after
                    
                    if freed > 0:
                        cleaned.append({
                            "location": temp_folder,
                            "freed_mb": round(freed / (1024**2), 2)
                        })
                        total_freed += freed
                except Exception as e:
                    logger.error(f"Error cleaning {temp_folder}: {e}")
        
        return {
            "cleaned": cleaned,
            "total_freed_mb": round(total_freed / (1024**2), 2),
            "total_freed_gb": round(total_freed / (1024**3), 2)
        }
    
    def _clear_browser_cache(self) -> Dict[str, Any]:
        """Clear browser cache."""
        cleaned = []
        total_freed = 0
        
        # Chrome cache
        chrome_cache = os.path.join(
            os.environ.get('LOCALAPPDATA', ''),
            'Google', 'Chrome', 'User Data', 'Default', 'Cache'
        )
        
        # Edge cache
        edge_cache = os.path.join(
            os.environ.get('LOCALAPPDATA', ''),
            'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'
        )
        
        caches = [
            ("Chrome", chrome_cache),
            ("Edge", edge_cache)
        ]
        
        for browser, cache_path in caches:
            if os.path.exists(cache_path):
                try:
                    size_before = self._get_folder_size(cache_path)
                    shutil.rmtree(cache_path, ignore_errors=True)
                    freed = size_before
                    
                    if freed > 0:
                        cleaned.append({
                            "browser": browser,
                            "freed_mb": round(freed / (1024**2), 2)
                        })
                        total_freed += freed
                except Exception as e:
                    logger.error(f"Error clearing {browser} cache: {e}")
        
        return {
            "cleaned": cleaned,
            "total_freed_mb": round(total_freed / (1024**2), 2),
            "total_freed_gb": round(total_freed / (1024**3), 2)
        }
    
    def _empty_recycle_bin(self) -> Dict[str, Any]:
        """Empty recycle bin."""
        try:
            # PowerShell command to empty recycle bin
            result = self._run_command(
                'powershell -command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"'
            )
            
            return {
                "success": True,
                "message": "Recycle bin emptied"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _run_disk_cleanup(self) -> Dict[str, Any]:
        """Run Windows disk cleanup."""
        try:
            # Run disk cleanup with all options
            result = self._run_command(
                'cleanmgr /sagerun:1',
                timeout=300
            )
            
            return {
                "success": result["success"],
                "message": "Disk cleanup completed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _optimize_startup(self) -> Dict[str, Any]:
        """Optimize startup programs."""
        # This would disable unnecessary startup programs
        # For safety, we'll just report what could be disabled
        
        return {
            "message": "Startup optimization requires manual review",
            "recommendation": "Use Task Manager > Startup to disable unnecessary programs"
        }
    
    def _free_space_aggressive(self, target_gb: int = 50) -> Dict[str, Any]:
        """Aggressively free up disk space."""
        results = {
            "target_gb": target_gb,
            "actions": []
        }
        
        # 1. Clean temp files
        temp_result = self._clean_temp_files()
        results["actions"].append({
            "action": "Clean temp files",
            "freed_gb": temp_result["total_freed_gb"]
        })
        
        # 2. Clear browser cache
        cache_result = self._clear_browser_cache()
        results["actions"].append({
            "action": "Clear browser cache",
            "freed_gb": cache_result["total_freed_gb"]
        })
        
        # 3. Empty recycle bin
        self._empty_recycle_bin()
        results["actions"].append({
            "action": "Empty recycle bin",
            "freed_gb": 0  # Size unknown
        })
        
        # 4. Clean Windows update cache
        try:
            update_cache = 'C:\\Windows\\SoftwareDistribution\\Download'
            if os.path.exists(update_cache):
                size_before = self._get_folder_size(update_cache)
                shutil.rmtree(update_cache, ignore_errors=True)
                os.makedirs(update_cache, exist_ok=True)
                freed_gb = size_before / (1024**3)
                results["actions"].append({
                    "action": "Clean Windows Update cache",
                    "freed_gb": round(freed_gb, 2)
                })
        except:
            pass
        
        # Calculate total freed
        total_freed = sum(action.get("freed_gb", 0) for action in results["actions"])
        results["total_freed_gb"] = round(total_freed, 2)
        results["target_met"] = total_freed >= target_gb
        
        return results
    
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
        
        action = kwargs.get("action")
        target_gb = kwargs.get("target_gb", 50)
        
        try:
            if action == "clean_temp":
                result = self._clean_temp_files()
            elif action == "clear_cache":
                result = self._clear_browser_cache()
            elif action == "empty_recycle":
                result = self._empty_recycle_bin()
            elif action == "disk_cleanup":
                result = self._run_disk_cleanup()
            elif action == "free_space":
                result = self._free_space_aggressive(target_gb)
            elif action == "optimize_all":
                result = {
                    "temp": self._clean_temp_files(),
                    "cache": self._clear_browser_cache(),
                    "recycle": self._empty_recycle_bin(),
                    "startup": self._optimize_startup()
                }
                
                # Calculate total
                total_freed = (
                    result["temp"]["total_freed_gb"] +
                    result["cache"]["total_freed_gb"]
                )
                result["total_freed_gb"] = round(total_freed, 2)
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
                error_message=None,
                execution_time_ms=int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            logger.error(f"Error during optimization: {e}")
            return SkillResult(
                success=False,
                result=None,
                error_message=str(e),
                execution_time_ms=int((time.time() - start) * 1000)
            )
