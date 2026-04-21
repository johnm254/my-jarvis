"""Demo script for Task 25.3: Monitoring and Logging

This script demonstrates the comprehensive monitoring and metrics tracking
implemented for the JARVIS system.

Validates: Requirements 19.6
"""

import logging
import time
from jarvis.metrics import get_metrics_tracker, MetricsContext
from jarvis.logging_config import setup_logging

# Set up logging with JSON formatting and rotation
setup_logging(log_level="INFO", log_dir="logs")

logger = logging.getLogger(__name__)


def simulate_conversation():
    """Simulate conversation response time tracking."""
    logger.info("=== Simulating Conversation Response Times ===")
    
    tracker = get_metrics_tracker()
    
    # Simulate 10 conversations with varying response times
    for i in range(10):
        with MetricsContext("conversation.response_time"):
            # Simulate processing time
            time.sleep(0.05 + (i * 0.01))  # 50ms to 140ms
        
        logger.info(f"Processed conversation {i+1}")
    
    # Get and display stats
    stats = tracker.get_latency_stats("conversation.response_time")
    if stats:
        logger.info(
            f"Conversation Response Time Stats: "
            f"p50={stats.p50:.2f}ms, p95={stats.p95:.2f}ms, p99={stats.p99:.2f}ms, "
            f"count={stats.count}"
        )


def simulate_skill_execution():
    """Simulate skill execution time tracking."""
    logger.info("\n=== Simulating Skill Execution Times ===")
    
    tracker = get_metrics_tracker()
    
    skills = ["web_search", "get_weather", "manage_calendar", "github_summary"]
    
    for skill in skills:
        # Simulate multiple executions
        for i in range(5):
            metric_name = f"skill.{skill}.execution_time"
            
            with MetricsContext(metric_name):
                # Simulate execution time (varies by skill)
                if skill == "web_search":
                    time.sleep(0.1 + (i * 0.02))  # 100-180ms
                elif skill == "get_weather":
                    time.sleep(0.05 + (i * 0.01))  # 50-90ms
                elif skill == "manage_calendar":
                    time.sleep(0.08 + (i * 0.015))  # 80-140ms
                else:  # github_summary
                    time.sleep(0.15 + (i * 0.03))  # 150-270ms
            
            # Record success/failure
            if i < 4:  # 80% success rate
                tracker.record_success(f"skill.{skill}")
            else:
                tracker.record_failure(f"skill.{skill}")
        
        # Display stats for this skill
        stats = tracker.get_latency_stats(metric_name)
        success_rate = tracker.get_success_rate(f"skill.{skill}")
        
        if stats and success_rate is not None:
            logger.info(
                f"{skill}: "
                f"p50={stats.p50:.2f}ms, p95={stats.p95:.2f}ms, p99={stats.p99:.2f}ms, "
                f"success_rate={success_rate:.1f}%"
            )


def simulate_memory_operations():
    """Simulate memory search latency tracking."""
    logger.info("\n=== Simulating Memory Search Operations ===")
    
    tracker = get_metrics_tracker()
    
    # Simulate 15 memory searches
    for i in range(15):
        with MetricsContext("memory.search_latency"):
            # Simulate search time (target < 500ms)
            time.sleep(0.1 + (i * 0.02))  # 100-380ms
        
        logger.info(f"Completed memory search {i+1}")
    
    # Get and display stats
    stats = tracker.get_latency_stats("memory.search_latency")
    if stats:
        logger.info(
            f"Memory Search Latency Stats: "
            f"p50={stats.p50:.2f}ms, p95={stats.p95:.2f}ms, p99={stats.p99:.2f}ms, "
            f"count={stats.count}"
        )
        
        if stats.p95 < 500:
            logger.info("✓ Memory search p95 is within 500ms target")
        else:
            logger.warning(f"✗ Memory search p95 ({stats.p95:.2f}ms) exceeds 500ms target")


def simulate_llm_api_calls():
    """Simulate LLM API call success rate tracking."""
    logger.info("\n=== Simulating LLM API Calls ===")
    
    tracker = get_metrics_tracker()
    
    # Simulate 20 LLM API calls
    for i in range(20):
        with MetricsContext("llm.api_call"):
            # Simulate API call time
            time.sleep(0.2 + (i * 0.01))  # 200-390ms
        
        # 95% success rate
        if i < 19:
            tracker.record_success("llm.api_call")
        else:
            tracker.record_failure("llm.api_call")
            logger.warning(f"LLM API call {i+1} failed")
    
    # Get and display stats
    stats = tracker.get_latency_stats("llm.api_call")
    success_rate = tracker.get_success_rate("llm.api_call")
    
    if stats and success_rate is not None:
        logger.info(
            f"LLM API Call Stats: "
            f"p50={stats.p50:.2f}ms, p95={stats.p95:.2f}ms, p99={stats.p99:.2f}ms, "
            f"success_rate={success_rate:.1f}%"
        )


def simulate_voice_interactions():
    """Simulate voice interaction success rate tracking."""
    logger.info("\n=== Simulating Voice Interactions ===")
    
    tracker = get_metrics_tracker()
    
    # Simulate STT operations
    for i in range(10):
        with MetricsContext("voice.stt"):
            time.sleep(0.3 + (i * 0.02))  # 300-480ms
        
        # 90% success rate
        if i < 9:
            tracker.record_success("voice.stt")
        else:
            tracker.record_failure("voice.stt")
            logger.warning(f"STT operation {i+1} failed")
    
    # Simulate TTS operations
    for i in range(10):
        with MetricsContext("voice.tts"):
            time.sleep(0.4 + (i * 0.03))  # 400-670ms
        
        # 95% success rate
        if i < 9 or i == 9:
            tracker.record_success("voice.tts")
        else:
            tracker.record_failure("voice.tts")
    
    # Display stats
    stt_stats = tracker.get_latency_stats("voice.stt")
    stt_success = tracker.get_success_rate("voice.stt")
    
    tts_stats = tracker.get_latency_stats("voice.tts")
    tts_success = tracker.get_success_rate("voice.tts")
    
    if stt_stats and stt_success is not None:
        logger.info(
            f"STT: p50={stt_stats.p50:.2f}ms, p95={stt_stats.p95:.2f}ms, "
            f"success_rate={stt_success:.1f}%"
        )
    
    if tts_stats and tts_success is not None:
        logger.info(
            f"TTS: p50={tts_stats.p50:.2f}ms, p95={tts_stats.p95:.2f}ms, "
            f"success_rate={tts_success:.1f}%"
        )


def simulate_hook_execution():
    """Simulate hook execution success rate tracking."""
    logger.info("\n=== Simulating Hook Executions ===")
    
    tracker = get_metrics_tracker()
    
    hooks = ["morning_brief", "calendar_reminder", "preference_learning"]
    
    for hook in hooks:
        # Simulate 5 executions per hook
        for i in range(5):
            metric_name = f"hook.{hook}.execution_time"
            
            with MetricsContext(metric_name):
                # Simulate execution time
                time.sleep(0.05 + (i * 0.01))
            
            # 100% success rate for hooks (they're reliable!)
            tracker.record_success(f"hook.{hook}")
        
        # Display stats
        stats = tracker.get_latency_stats(metric_name)
        success_rate = tracker.get_success_rate(f"hook.{hook}")
        
        if stats and success_rate is not None:
            logger.info(
                f"{hook}: "
                f"p50={stats.p50:.2f}ms, success_rate={success_rate:.1f}%"
            )


def display_summary():
    """Display comprehensive metrics summary."""
    logger.info("\n" + "="*70)
    logger.info("=== COMPREHENSIVE METRICS SUMMARY ===")
    logger.info("="*70)
    
    tracker = get_metrics_tracker()
    tracker.log_metrics_summary()
    
    logger.info("\n" + "="*70)
    logger.info("Monitoring and logging demonstration complete!")
    logger.info("="*70)
    
    logger.info("\nLog files created:")
    logger.info("  - logs/app.log (structured JSON logs with all events)")
    logger.info("  - logs/error.log (errors only)")
    logger.info("  - logs/audit.log (audit events)")
    logger.info("\nLog rotation: Daily, keeping 30 days of history")


def main():
    """Run the monitoring demonstration."""
    logger.info("="*70)
    logger.info("JARVIS Monitoring and Logging Demonstration")
    logger.info("Task 25.3: Implement monitoring and logging")
    logger.info("="*70)
    
    # Simulate various system operations
    simulate_conversation()
    simulate_skill_execution()
    simulate_memory_operations()
    simulate_llm_api_calls()
    simulate_voice_interactions()
    simulate_hook_execution()
    
    # Display comprehensive summary
    display_summary()


if __name__ == "__main__":
    main()
