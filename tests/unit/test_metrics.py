"""Unit tests for metrics tracking system."""

import unittest
from jarvis.metrics import MetricsTracker, MetricsContext, get_metrics_tracker, reset_metrics_tracker
import time


class TestMetricsTracker(unittest.TestCase):
    """Test cases for MetricsTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = MetricsTracker(max_samples=100)
    
    def test_record_latency(self):
        """Test recording latency metrics."""
        self.tracker.record_latency("test.metric", 100.0)
        self.tracker.record_latency("test.metric", 200.0)
        self.tracker.record_latency("test.metric", 150.0)
        
        stats = self.tracker.get_latency_stats("test.metric")
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats.count, 3)
        self.assertEqual(stats.min, 100.0)
        self.assertEqual(stats.max, 200.0)
        self.assertEqual(stats.mean, 150.0)
    
    def test_record_success_failure(self):
        """Test recording success and failure metrics."""
        self.tracker.record_success("test.operation")
        self.tracker.record_success("test.operation")
        self.tracker.record_success("test.operation")
        self.tracker.record_failure("test.operation")
        
        success_rate = self.tracker.get_success_rate("test.operation")
        
        self.assertIsNotNone(success_rate)
        self.assertEqual(success_rate, 75.0)  # 3 successes out of 4 total
    
    def test_percentile_calculation(self):
        """Test percentile calculations."""
        # Add 100 samples from 1 to 100
        for i in range(1, 101):
            self.tracker.record_latency("test.percentile", float(i))
        
        stats = self.tracker.get_latency_stats("test.percentile")
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats.count, 100)
        self.assertAlmostEqual(stats.p50, 50.5, delta=1.0)
        self.assertAlmostEqual(stats.p95, 95.05, delta=1.0)
        self.assertAlmostEqual(stats.p99, 99.01, delta=1.0)
    
    def test_max_samples_limit(self):
        """Test that max_samples limit is enforced."""
        tracker = MetricsTracker(max_samples=10)
        
        # Add 20 samples
        for i in range(20):
            tracker.record_latency("test.limit", float(i))
        
        stats = tracker.get_latency_stats("test.limit")
        
        # Should only keep last 10 samples
        self.assertEqual(stats.count, 10)
        self.assertEqual(stats.min, 10.0)  # First 10 samples were dropped
        self.assertEqual(stats.max, 19.0)
    
    def test_get_all_metrics(self):
        """Test getting all metrics."""
        self.tracker.record_latency("metric1", 100.0)
        self.tracker.record_latency("metric1", 200.0)
        
        self.tracker.record_success("metric2")
        self.tracker.record_failure("metric2")
        
        all_metrics = self.tracker.get_all_metrics()
        
        self.assertIn("metric1", all_metrics)
        self.assertIn("metric2", all_metrics)
        self.assertEqual(all_metrics["metric1"]["type"], "latency")
        self.assertEqual(all_metrics["metric2"]["type"], "success_rate")
    
    def test_reset_metrics(self):
        """Test resetting metrics."""
        self.tracker.record_latency("test.reset", 100.0)
        self.tracker.record_success("test.reset")
        
        # Reset specific metric
        self.tracker.reset_metrics("test.reset")
        
        stats = self.tracker.get_latency_stats("test.reset")
        success_rate = self.tracker.get_success_rate("test.reset")
        
        self.assertIsNone(stats)
        self.assertIsNone(success_rate)
    
    def test_reset_all_metrics(self):
        """Test resetting all metrics."""
        self.tracker.record_latency("metric1", 100.0)
        self.tracker.record_latency("metric2", 200.0)
        
        self.tracker.reset_metrics()
        
        all_metrics = self.tracker.get_all_metrics()
        self.assertEqual(len(all_metrics), 0)


class TestMetricsContext(unittest.TestCase):
    """Test cases for MetricsContext context manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = MetricsTracker()
    
    def test_metrics_context(self):
        """Test MetricsContext records latency."""
        with MetricsContext("test.context", self.tracker):
            time.sleep(0.01)  # Sleep for 10ms
        
        stats = self.tracker.get_latency_stats("test.context")
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats.count, 1)
        self.assertGreaterEqual(stats.min, 10.0)  # At least 10ms
    
    def test_metrics_context_with_exception(self):
        """Test MetricsContext records latency even with exceptions."""
        try:
            with MetricsContext("test.exception", self.tracker):
                time.sleep(0.01)
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        stats = self.tracker.get_latency_stats("test.exception")
        
        # Should still record the latency
        self.assertIsNotNone(stats)
        self.assertEqual(stats.count, 1)


class TestGlobalMetricsTracker(unittest.TestCase):
    """Test cases for global metrics tracker."""
    
    def setUp(self):
        """Reset global tracker before each test."""
        reset_metrics_tracker()
    
    def test_get_global_tracker(self):
        """Test getting global metrics tracker."""
        tracker1 = get_metrics_tracker()
        tracker2 = get_metrics_tracker()
        
        # Should return the same instance
        self.assertIs(tracker1, tracker2)
    
    def test_reset_global_tracker(self):
        """Test resetting global metrics tracker."""
        tracker1 = get_metrics_tracker()
        tracker1.record_latency("test", 100.0)
        
        reset_metrics_tracker()
        
        tracker2 = get_metrics_tracker()
        
        # Should be a new instance
        self.assertIsNot(tracker1, tracker2)
        
        # New tracker should have no metrics
        stats = tracker2.get_latency_stats("test")
        self.assertIsNone(stats)


if __name__ == "__main__":
    unittest.main()
