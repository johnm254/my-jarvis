"""Metrics tracking and monitoring for JARVIS.

This module provides comprehensive metrics tracking for all system components:
- Conversation response times (p50, p95, p99)
- Skill execution times per skill
- Memory search latency
- LLM API call success rate
- Voice interaction success rate
- Hook execution success rate

Validates: Requirements 19.6
"""

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Deque
from threading import Lock
import statistics

logger = logging.getLogger(__name__)


@dataclass
class MetricSample:
    """A single metric sample with timestamp."""
    value: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MetricStats:
    """Statistical summary of a metric."""
    count: int
    min: float
    max: float
    mean: float
    p50: float
    p95: float
    p99: float
    success_rate: Optional[float] = None


class MetricsTracker:
    """
    Centralized metrics tracking for JARVIS system.
    
    Tracks performance metrics and success rates for all major components.
    Provides percentile calculations (p50, p95, p99) for latency metrics.
    
    Thread-safe for concurrent metric recording.
    """
    
    def __init__(self, max_samples: int = 1000):
        """
        Initialize the metrics tracker.
        
        Args:
            max_samples: Maximum number of samples to keep per metric (default: 1000)
        """
        self.max_samples = max_samples
        
        # Latency metrics (milliseconds)
        self._latency_metrics: Dict[str, Deque[float]] = defaultdict(
            lambda: deque(maxlen=max_samples)
        )
        
        # Success/failure counters
        self._success_counters: Dict[str, int] = defaultdict(int)
        self._failure_counters: Dict[str, int] = defaultdict(int)
        
        # Thread safety
        self._lock = Lock()
        
        logger.info(f"MetricsTracker initialized with max_samples={max_samples}")
    
    def record_latency(self, metric_name: str, latency_ms: float) -> None:
        """
        Record a latency measurement.
        
        Args:
            metric_name: Name of the metric (e.g., "conversation.response_time")
            latency_ms: Latency in milliseconds
        """
        with self._lock:
            self._latency_metrics[metric_name].append(latency_ms)
            
            # Log slow operations
            if latency_ms > 1000:  # > 1 second
                logger.warning(
                    f"Slow operation detected: {metric_name} took {latency_ms:.2f}ms",
                    extra={"extra_fields": {
                        "metric_name": metric_name,
                        "latency_ms": latency_ms,
                        "metric_type": "latency"
                    }}
                )
    
    def record_success(self, metric_name: str) -> None:
        """
        Record a successful operation.
        
        Args:
            metric_name: Name of the metric (e.g., "llm.api_call")
        """
        with self._lock:
            self._success_counters[metric_name] += 1
    
    def record_failure(self, metric_name: str) -> None:
        """
        Record a failed operation.
        
        Args:
            metric_name: Name of the metric (e.g., "llm.api_call")
        """
        with self._lock:
            self._failure_counters[metric_name] += 1
            
            # Log failures
            logger.warning(
                f"Operation failure recorded: {metric_name}",
                extra={"extra_fields": {
                    "metric_name": metric_name,
                    "metric_type": "failure"
                }}
            )
    
    def get_latency_stats(self, metric_name: str) -> Optional[MetricStats]:
        """
        Get statistical summary for a latency metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            MetricStats with percentiles, or None if no data
        """
        with self._lock:
            samples = list(self._latency_metrics.get(metric_name, []))
            
            if not samples:
                return None
            
            sorted_samples = sorted(samples)
            count = len(sorted_samples)
            
            return MetricStats(
                count=count,
                min=min(sorted_samples),
                max=max(sorted_samples),
                mean=statistics.mean(sorted_samples),
                p50=self._percentile(sorted_samples, 50),
                p95=self._percentile(sorted_samples, 95),
                p99=self._percentile(sorted_samples, 99)
            )
    
    def get_success_rate(self, metric_name: str) -> Optional[float]:
        """
        Get success rate for a metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Success rate as a percentage (0-100), or None if no data
        """
        with self._lock:
            successes = self._success_counters.get(metric_name, 0)
            failures = self._failure_counters.get(metric_name, 0)
            total = successes + failures
            
            if total == 0:
                return None
            
            return (successes / total) * 100.0
    
    def get_all_metrics(self) -> Dict[str, Dict]:
        """
        Get all tracked metrics.
        
        Returns:
            Dictionary with all metrics and their statistics
        """
        with self._lock:
            metrics = {}
            
            # Add latency metrics
            for metric_name in self._latency_metrics.keys():
                stats = self.get_latency_stats(metric_name)
                if stats:
                    metrics[metric_name] = {
                        "type": "latency",
                        "count": stats.count,
                        "min_ms": stats.min,
                        "max_ms": stats.max,
                        "mean_ms": stats.mean,
                        "p50_ms": stats.p50,
                        "p95_ms": stats.p95,
                        "p99_ms": stats.p99
                    }
            
            # Add success rate metrics
            all_metric_names = set(self._success_counters.keys()) | set(self._failure_counters.keys())
            for metric_name in all_metric_names:
                success_rate = self.get_success_rate(metric_name)
                if success_rate is not None:
                    successes = self._success_counters.get(metric_name, 0)
                    failures = self._failure_counters.get(metric_name, 0)
                    
                    metrics[metric_name] = {
                        "type": "success_rate",
                        "success_count": successes,
                        "failure_count": failures,
                        "total_count": successes + failures,
                        "success_rate_percent": success_rate
                    }
            
            return metrics
    
    def log_metrics_summary(self) -> None:
        """Log a summary of all metrics."""
        metrics = self.get_all_metrics()
        
        if not metrics:
            logger.info("No metrics data available")
            return
        
        logger.info("=== Metrics Summary ===")
        
        # Group by type
        latency_metrics = {k: v for k, v in metrics.items() if v.get("type") == "latency"}
        success_metrics = {k: v for k, v in metrics.items() if v.get("type") == "success_rate"}
        
        if latency_metrics:
            logger.info("Latency Metrics:")
            for name, stats in latency_metrics.items():
                logger.info(
                    f"  {name}: "
                    f"p50={stats['p50_ms']:.2f}ms, "
                    f"p95={stats['p95_ms']:.2f}ms, "
                    f"p99={stats['p99_ms']:.2f}ms, "
                    f"count={stats['count']}"
                )
        
        if success_metrics:
            logger.info("Success Rate Metrics:")
            for name, stats in success_metrics.items():
                logger.info(
                    f"  {name}: "
                    f"{stats['success_rate_percent']:.2f}% "
                    f"({stats['success_count']}/{stats['total_count']})"
                )
    
    def reset_metrics(self, metric_name: Optional[str] = None) -> None:
        """
        Reset metrics data.
        
        Args:
            metric_name: Specific metric to reset, or None to reset all
        """
        with self._lock:
            if metric_name:
                if metric_name in self._latency_metrics:
                    self._latency_metrics[metric_name].clear()
                if metric_name in self._success_counters:
                    self._success_counters[metric_name] = 0
                if metric_name in self._failure_counters:
                    self._failure_counters[metric_name] = 0
                logger.info(f"Reset metrics for: {metric_name}")
            else:
                self._latency_metrics.clear()
                self._success_counters.clear()
                self._failure_counters.clear()
                logger.info("Reset all metrics")
    
    @staticmethod
    def _percentile(sorted_data: List[float], percentile: float) -> float:
        """
        Calculate percentile from sorted data.
        
        Args:
            sorted_data: Sorted list of values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        if not sorted_data:
            return 0.0
        
        if len(sorted_data) == 1:
            return sorted_data[0]
        
        # Use linear interpolation between closest ranks
        rank = (percentile / 100.0) * (len(sorted_data) - 1)
        lower_index = int(rank)
        upper_index = min(lower_index + 1, len(sorted_data) - 1)
        fraction = rank - lower_index
        
        return sorted_data[lower_index] + fraction * (sorted_data[upper_index] - sorted_data[lower_index])


# Global metrics tracker instance
_global_metrics_tracker: Optional[MetricsTracker] = None


def get_metrics_tracker() -> MetricsTracker:
    """
    Get the global metrics tracker instance.
    
    Returns:
        Global MetricsTracker instance
    """
    global _global_metrics_tracker
    
    if _global_metrics_tracker is None:
        _global_metrics_tracker = MetricsTracker()
    
    return _global_metrics_tracker


def reset_metrics_tracker() -> None:
    """Reset the global metrics tracker (useful for testing)."""
    global _global_metrics_tracker
    _global_metrics_tracker = None


class MetricsContext:
    """
    Context manager for tracking operation latency.
    
    Usage:
        with MetricsContext("conversation.response_time"):
            # ... perform operation ...
            pass
    """
    
    def __init__(self, metric_name: str, tracker: Optional[MetricsTracker] = None):
        """
        Initialize metrics context.
        
        Args:
            metric_name: Name of the metric to track
            tracker: Optional MetricsTracker instance (uses global if None)
        """
        self.metric_name = metric_name
        self.tracker = tracker or get_metrics_tracker()
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Record latency."""
        if self.start_time is not None:
            latency_ms = (time.time() - self.start_time) * 1000
            self.tracker.record_latency(self.metric_name, latency_ms)
        
        # Don't suppress exceptions
        return False
