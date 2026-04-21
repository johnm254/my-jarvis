"""Hooks Engine for JARVIS - Automated behaviors triggered by time or events.

Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5
"""

import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.job import Job
from jarvis.metrics import get_metrics_tracker

logger = logging.getLogger(__name__)


@dataclass
class Hook:
    """
    Represents a hook that can be scheduled or triggered by events.
    
    Attributes:
        id: Unique identifier for the hook
        name: Human-readable name
        description: Description of what the hook does
        hook_type: Type of hook ('cron', 'interval', 'event')
        trigger: Trigger configuration (cron expression, interval seconds, or event name)
        callback: Function to execute when hook is triggered
        enabled: Whether the hook is currently active
    """
    id: str
    name: str
    description: str
    hook_type: str  # 'cron', 'interval', 'event'
    trigger: str  # Cron expression, interval seconds, or event name
    callback: Callable
    enabled: bool = True


class HooksEngine:
    """
    Manages automated behaviors triggered by time or events.
    
    Supports:
    - Time-based hooks (cron schedules)
    - Interval-based hooks (periodic execution)
    - Event-based hooks (triggered by system events)
    
    Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5
    """
    
    def __init__(self):
        """Initialize the hooks engine with a background scheduler."""
        self._hooks: Dict[str, Hook] = {}
        self._scheduler = BackgroundScheduler()
        self._scheduler.start()
        self.metrics_tracker = get_metrics_tracker()
        logger.info("HooksEngine initialized with background scheduler")
    
    def register_hook(self, hook: Hook) -> None:
        """
        Register a hook for execution.
        
        Args:
            hook: Hook to register
            
        Raises:
            ValueError: If hook with same ID already exists or invalid hook type
        """
        if hook.id in self._hooks:
            logger.warning(f"Hook '{hook.id}' already registered, replacing")
        
        # Validate hook type
        if hook.hook_type not in ['cron', 'interval', 'event']:
            raise ValueError(
                f"Invalid hook type '{hook.hook_type}'. "
                f"Must be 'cron', 'interval', or 'event'"
            )
        
        # Store the hook
        self._hooks[hook.id] = hook
        
        # Schedule the hook if it's time-based or interval-based
        if hook.enabled:
            if hook.hook_type == 'cron':
                self._schedule_cron_hook(hook)
            elif hook.hook_type == 'interval':
                self._schedule_interval_hook(hook)
            # Event-based hooks are not scheduled, they're triggered manually
        
        logger.info(
            f"Registered hook '{hook.name}' (ID: {hook.id}, Type: {hook.hook_type})"
        )
    
    def _schedule_cron_hook(self, hook: Hook) -> None:
        """
        Schedule a cron-based hook.
        
        Args:
            hook: Hook with cron trigger
        """
        try:
            # Parse cron expression
            # Format: "minute hour day month day_of_week"
            # Example: "0 7 * * *" = Every day at 7:00 AM
            parts = hook.trigger.split()
            if len(parts) != 5:
                raise ValueError(
                    f"Invalid cron expression '{hook.trigger}'. "
                    f"Expected format: 'minute hour day month day_of_week'"
                )
            
            minute, hour, day, month, day_of_week = parts
            
            # Create cron trigger
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            )
            
            # Add job to scheduler
            self._scheduler.add_job(
                func=self._execute_hook_wrapper,
                trigger=trigger,
                args=[hook.id],
                id=hook.id,
                name=hook.name,
                replace_existing=True
            )
            
            logger.info(f"Scheduled cron hook '{hook.name}' with trigger: {hook.trigger}")
            
        except Exception as e:
            logger.error(f"Failed to schedule cron hook '{hook.name}': {e}")
            raise
    
    def _schedule_interval_hook(self, hook: Hook) -> None:
        """
        Schedule an interval-based hook.
        
        Args:
            hook: Hook with interval trigger (seconds)
        """
        try:
            # Parse interval (should be integer seconds)
            interval_seconds = int(hook.trigger)
            
            if interval_seconds <= 0:
                raise ValueError(f"Interval must be positive, got {interval_seconds}")
            
            # Create interval trigger
            trigger = IntervalTrigger(seconds=interval_seconds)
            
            # Add job to scheduler
            self._scheduler.add_job(
                func=self._execute_hook_wrapper,
                trigger=trigger,
                args=[hook.id],
                id=hook.id,
                name=hook.name,
                replace_existing=True
            )
            
            logger.info(
                f"Scheduled interval hook '{hook.name}' "
                f"to run every {interval_seconds} seconds"
            )
            
        except ValueError as e:
            logger.error(f"Invalid interval for hook '{hook.name}': {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to schedule interval hook '{hook.name}': {e}")
            raise
    
    def _execute_hook_wrapper(self, hook_id: str) -> None:
        """
        Wrapper for hook execution with error handling and logging.
        
        Args:
            hook_id: ID of the hook to execute
        """
        hook = self._hooks.get(hook_id)
        if not hook:
            logger.error(f"Hook '{hook_id}' not found")
            self.metrics_tracker.record_failure(f"hook.{hook_id}")
            return
        
        if not hook.enabled:
            logger.debug(f"Hook '{hook.name}' is disabled, skipping execution")
            return
        
        try:
            logger.info(f"Executing hook '{hook.name}' (ID: {hook_id})")
            start_time = datetime.now()
            
            # Execute the hook callback
            hook.callback()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            execution_time_ms = execution_time * 1000
            
            # Record metrics
            self.metrics_tracker.record_latency(f"hook.{hook_id}.execution_time", execution_time_ms)
            self.metrics_tracker.record_success(f"hook.{hook_id}")
            
            logger.info(
                f"Hook '{hook.name}' executed successfully "
                f"in {execution_time:.2f} seconds"
            )
            
        except Exception as e:
            # Record failure
            self.metrics_tracker.record_failure(f"hook.{hook_id}")
            
            logger.error(
                f"Hook '{hook.name}' execution failed: {e}",
                exc_info=True
            )
    
    def execute_hook(self, hook_id: str) -> None:
        """
        Manually execute a hook (useful for event-based hooks).
        
        Args:
            hook_id: ID of the hook to execute
            
        Raises:
            ValueError: If hook not found
        """
        if hook_id not in self._hooks:
            raise ValueError(f"Hook '{hook_id}' not found")
        
        self._execute_hook_wrapper(hook_id)
    
    def unregister_hook(self, hook_id: str) -> None:
        """
        Unregister a hook and remove it from the scheduler.
        
        Args:
            hook_id: ID of the hook to unregister
        """
        if hook_id not in self._hooks:
            logger.warning(f"Hook '{hook_id}' not found, cannot unregister")
            return
        
        hook = self._hooks[hook_id]
        
        # Remove from scheduler if it's a scheduled hook
        if hook.hook_type in ['cron', 'interval']:
            try:
                self._scheduler.remove_job(hook_id)
                logger.info(f"Removed scheduled job for hook '{hook.name}'")
            except Exception as e:
                logger.warning(f"Failed to remove scheduled job: {e}")
        
        # Remove from hooks dictionary
        del self._hooks[hook_id]
        logger.info(f"Unregistered hook '{hook.name}' (ID: {hook_id})")
    
    def enable_hook(self, hook_id: str) -> None:
        """
        Enable a disabled hook.
        
        Args:
            hook_id: ID of the hook to enable
            
        Raises:
            ValueError: If hook not found
        """
        if hook_id not in self._hooks:
            raise ValueError(f"Hook '{hook_id}' not found")
        
        hook = self._hooks[hook_id]
        
        if hook.enabled:
            logger.debug(f"Hook '{hook.name}' is already enabled")
            return
        
        hook.enabled = True
        
        # Reschedule if it's a time-based or interval-based hook
        if hook.hook_type == 'cron':
            self._schedule_cron_hook(hook)
        elif hook.hook_type == 'interval':
            self._schedule_interval_hook(hook)
        
        logger.info(f"Enabled hook '{hook.name}' (ID: {hook_id})")
    
    def disable_hook(self, hook_id: str) -> None:
        """
        Disable an enabled hook without unregistering it.
        
        Args:
            hook_id: ID of the hook to disable
            
        Raises:
            ValueError: If hook not found
        """
        if hook_id not in self._hooks:
            raise ValueError(f"Hook '{hook_id}' not found")
        
        hook = self._hooks[hook_id]
        
        if not hook.enabled:
            logger.debug(f"Hook '{hook.name}' is already disabled")
            return
        
        hook.enabled = False
        
        # Remove from scheduler if it's a scheduled hook
        if hook.hook_type in ['cron', 'interval']:
            try:
                self._scheduler.remove_job(hook_id)
                logger.info(f"Removed scheduled job for hook '{hook.name}'")
            except Exception as e:
                logger.warning(f"Failed to remove scheduled job: {e}")
        
        logger.info(f"Disabled hook '{hook.name}' (ID: {hook_id})")
    
    def list_active_hooks(self) -> List[Hook]:
        """
        List all active (enabled) hooks.
        
        Returns:
            List of enabled hooks
        """
        return [hook for hook in self._hooks.values() if hook.enabled]
    
    def list_all_hooks(self) -> List[Hook]:
        """
        List all registered hooks (enabled and disabled).
        
        Returns:
            List of all hooks
        """
        return list(self._hooks.values())
    
    def get_hook(self, hook_id: str) -> Optional[Hook]:
        """
        Get a hook by ID.
        
        Args:
            hook_id: ID of the hook to retrieve
            
        Returns:
            Hook if found, None otherwise
        """
        return self._hooks.get(hook_id)
    
    def shutdown(self) -> None:
        """
        Shutdown the hooks engine and stop all scheduled jobs.
        """
        logger.info("Shutting down HooksEngine...")
        self._scheduler.shutdown(wait=True)
        logger.info("HooksEngine shutdown complete")
