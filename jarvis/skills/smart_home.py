"""Smart Home Control Skill for JARVIS using Home Assistant REST API.

Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5
"""

import os
import time
from typing import Any, Dict, Optional
import requests

from jarvis.skills.base import Skill, SkillResult


class SmartHomeSkill(Skill):
    """
    Smart home control skill that integrates with Home Assistant REST API.
    
    Sends commands to smart home devices and returns current device state.
    
    Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5
    """
    
    def __init__(self):
        """Initialize the smart home control skill."""
        super().__init__()
        self._name = "smart_home"
        self._description = "Control smart home devices via Home Assistant. Send commands to devices and retrieve their current state."
        self._parameters = {
            "type": "object",
            "properties": {
                "device": {
                    "type": "string",
                    "description": "The device entity ID to control (e.g., 'light.living_room', 'switch.bedroom_fan')"
                },
                "action": {
                    "type": "string",
                    "description": "The action to perform on the device (e.g., 'turn_on', 'turn_off', 'toggle', 'set_brightness')"
                },
                "parameters": {
                    "type": "object",
                    "description": "Optional parameters for the action (e.g., brightness level, temperature)",
                    "additionalProperties": True
                }
            },
            "required": ["device", "action"]
        }
        
        # Home Assistant configuration from environment
        self._ha_url = os.getenv("HOME_ASSISTANT_URL")
        self._ha_token = os.getenv("HOME_ASSISTANT_TOKEN")
        self._timeout = 5  # 5 seconds timeout
    
    def _check_configuration(self) -> tuple[bool, Optional[str]]:
        """
        Check if Home Assistant is configured.
        
        Returns:
            Tuple of (is_configured, error_message)
        """
        if not self._ha_url:
            return False, "Home Assistant URL not configured. Please set HOME_ASSISTANT_URL in .env file."
        
        if not self._ha_token:
            return False, "Home Assistant token not configured. Please set HOME_ASSISTANT_TOKEN in .env file."
        
        return True, None
    
    def _get_device_state(self, device: str) -> tuple[bool, Any, Optional[str]]:
        """
        Get the current state of a device.
        
        Args:
            device: Device entity ID
            
        Returns:
            Tuple of (success, state_data, error_message)
        """
        try:
            headers = {
                "Authorization": f"Bearer {self._ha_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self._ha_url}/api/states/{device}"
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self._timeout
            )
            
            if response.status_code == 404:
                return False, None, f"Device '{device}' not found in Home Assistant"
            
            if response.status_code != 200:
                return False, None, f"Home Assistant API returned status code {response.status_code}: {response.text}"
            
            state_data = response.json()
            
            return True, {
                "entity_id": state_data.get("entity_id"),
                "state": state_data.get("state"),
                "attributes": state_data.get("attributes", {}),
                "last_changed": state_data.get("last_changed"),
                "last_updated": state_data.get("last_updated")
            }, None
            
        except requests.exceptions.Timeout:
            return False, None, f"Request to Home Assistant timed out after {self._timeout} seconds"
        except requests.exceptions.RequestException as e:
            return False, None, f"Network error communicating with Home Assistant: {str(e)}"
        except Exception as e:
            return False, None, f"Error getting device state: {str(e)}"
    
    def _send_command(
        self,
        device: str,
        action: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Any, Optional[str]]:
        """
        Send a command to a device.
        
        Args:
            device: Device entity ID
            action: Action to perform
            parameters: Optional parameters for the action
            
        Returns:
            Tuple of (success, result, error_message)
        """
        try:
            headers = {
                "Authorization": f"Bearer {self._ha_token}",
                "Content-Type": "application/json"
            }
            
            # Parse device domain from entity_id (e.g., "light" from "light.living_room")
            if "." not in device:
                return False, None, f"Invalid device entity ID format: {device}. Expected format: 'domain.entity' (e.g., 'light.living_room')"
            
            domain = device.split(".")[0]
            
            # Build service call URL
            url = f"{self._ha_url}/api/services/{domain}/{action}"
            
            # Build request payload
            payload = {
                "entity_id": device
            }
            
            # Add optional parameters
            if parameters:
                payload.update(parameters)
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self._timeout
            )
            
            if response.status_code == 404:
                return False, None, f"Service '{domain}.{action}' not found in Home Assistant"
            
            if response.status_code != 200:
                return False, None, f"Home Assistant API returned status code {response.status_code}: {response.text}"
            
            # Command sent successfully
            return True, {
                "device": device,
                "action": action,
                "status": "command_sent"
            }, None
            
        except requests.exceptions.Timeout:
            return False, None, f"Request to Home Assistant timed out after {self._timeout} seconds"
        except requests.exceptions.RequestException as e:
            return False, None, f"Network error communicating with Home Assistant: {str(e)}"
        except Exception as e:
            return False, None, f"Error sending command: {str(e)}"
    
    def execute(self, **kwargs) -> SkillResult:
        """
        Execute smart home control action.
        
        Args:
            **kwargs: Must contain 'device' and 'action' parameters, optional 'parameters'
            
        Returns:
            SkillResult with command result and device state
            
        Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5
        """
        start_time = time.time()
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(**kwargs)
        if not is_valid:
            return SkillResult(
                success=False,
                result=None,
                error_message=error_msg,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        device = kwargs.get("device")
        action = kwargs.get("action")
        parameters = kwargs.get("parameters")
        
        # Check configuration (requirement 9.2)
        config_ok, config_error = self._check_configuration()
        if not config_ok:
            return SkillResult(
                success=False,
                result=None,
                error_message=config_error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Send command to device (requirement 9.3)
        command_success, command_result, command_error = self._send_command(
            device, action, parameters
        )
        
        if not command_success:
            # If device is unavailable, return error (requirement 9.5)
            return SkillResult(
                success=False,
                result=None,
                error_message=command_error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Get device state after action (requirement 9.4)
        # Wait a brief moment for state to update
        time.sleep(0.5)
        
        state_success, state_data, state_error = self._get_device_state(device)
        
        execution_time = int((time.time() - start_time) * 1000)
        
        # Combine command result with device state
        result = {
            "command": command_result,
            "device_state": state_data if state_success else None
        }
        
        if not state_success:
            # Command succeeded but couldn't get state - still return success
            # but include state error in result
            result["state_error"] = state_error
        
        return SkillResult(
            success=True,
            result=result,
            error_message=None,
            execution_time_ms=execution_time
        )
