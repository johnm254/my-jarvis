"""Hooks module - Automated behaviors and scheduled tasks."""

from jarvis.hooks.hooks_engine import HooksEngine, Hook
from jarvis.hooks.morning_brief_hook import MorningBriefHook, create_morning_brief_hook
from jarvis.hooks.preference_learning_hook import PreferenceLearningHook, create_preference_learning_hook
from jarvis.hooks.calendar_reminder_hook import CalendarReminderHook, create_calendar_reminder_hook
from jarvis.hooks.reminder_delivery_hook import ReminderDeliveryHook, create_reminder_delivery_hook

__all__ = [
    "HooksEngine",
    "Hook",
    "MorningBriefHook",
    "create_morning_brief_hook",
    "PreferenceLearningHook",
    "create_preference_learning_hook",
    "CalendarReminderHook",
    "create_calendar_reminder_hook",
    "ReminderDeliveryHook",
    "create_reminder_delivery_hook",
]
