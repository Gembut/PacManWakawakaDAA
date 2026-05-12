"""
Algorithm Analysis and Metrics Tracking
Tracks performance statistics for pathfinding algorithms
"""

import time
from collections import defaultdict


class AlgorithmMetrics:
    """Tracks performance metrics for different pathfinding algorithms"""

    def __init__(self):
        self.metrics = defaultdict(
            lambda: {
                "calls": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "total_path_length": 0,
                "avg_path_length": 0.0,
                "nodes_explored": 0,
                "avg_nodes_explored": 0.0,
                "successful_paths": 0,
                "failed_searches": 0,
            }
        )

    def record_search(
        self, algorithm_name, execution_time, path_length, nodes_explored, success=True
    ):
        """Record metrics for a pathfinding search"""
        metrics = self.metrics[algorithm_name]
        metrics["calls"] += 1
        metrics["total_time"] += execution_time
        metrics["avg_time"] = metrics["total_time"] / metrics["calls"]

        if success:
            metrics["successful_paths"] += 1
            metrics["total_path_length"] += path_length
            metrics["avg_path_length"] = (
                metrics["total_path_length"] / metrics["successful_paths"]
            )
        else:
            metrics["failed_searches"] += 1

        metrics["nodes_explored"] += nodes_explored
        metrics["avg_nodes_explored"] = metrics["nodes_explored"] / metrics["calls"]

    def get_algorithm_names(self):
        """Get list of algorithms with recorded metrics"""
        return list(self.metrics.keys())

    def get_summary(self, algorithm_name):
        """Get summary statistics for an algorithm"""
        return self.metrics.get(algorithm_name, None)

    def get_all_summaries(self):
        """Get summary statistics for all algorithms"""
        return dict(self.metrics)

    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics.clear()


# Global metrics tracker
global_metrics = AlgorithmMetrics()


def track_pathfinding(algorithm_name):
    """Decorator to track pathfinding algorithm performance"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()

            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
            path_length = len(result) if result else 0
            nodes_explored = len(result) if result else 0  # Simplified metric

            success = len(result) > 0
            global_metrics.record_search(
                algorithm_name, execution_time, path_length, nodes_explored, success
            )

            return result

        return wrapper

    return decorator
