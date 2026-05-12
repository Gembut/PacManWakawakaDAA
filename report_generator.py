"""
Algorithm Report Generator
Generates comprehensive reports for the PAC-MAN game project
Shows which algorithms are used and their performance metrics
"""

from datetime import datetime
from algorithm.analysis import global_metrics


class AlgorithmReport:
    """Generates detailed reports about algorithm implementation and performance"""

    ALGORITHM_DESCRIPTIONS = {
        "astar": {
            "name": "A* (A-Star)",
            "description": "Informed search algorithm using heuristic (grid distance) to guide pathfinding",
            "time_complexity": "O((V + E) log V)",
            "space_complexity": "O(V)",
            "uses_heuristic": True,
            "optimal": True,
            "characteristics": [
                "Uses heuristic (grid distance) to estimate distance to goal",
                "More efficient than Dijkstra for pathfinding",
                "Guaranteed to find shortest path if heuristic is admissible",
                "Perfect for single target pathfinding (player location)",
            ],
        },
        "dijkstra": {
            "name": "Dijkstra's Algorithm",
            "description": "Uniform cost search that finds shortest path from start to all reachable nodes",
            "time_complexity": "O((V + E) log V)",
            "space_complexity": "O(V)",
            "uses_heuristic": False,
            "optimal": True,
            "characteristics": [
                "Explores nodes in order of cost from start",
                "No heuristic information used",
                "Guaranteed shortest path on graphs with non-negative weights",
                "Slower than A* but more flexible",
                "Good for scenarios without specific target",
            ],
        },
        "bfs": {
            "name": "Breadth-First Search (BFS)",
            "description": "Explores all nodes at current depth before moving deeper",
            "time_complexity": "O(V + E)",
            "space_complexity": "O(V)",
            "uses_heuristic": False,
            "optimal": True,
            "characteristics": [
                "Explores level by level (breadth first)",
                "Optimal for unweighted graphs",
                "Lower computational cost than Dijkstra",
                "Balanced exploration pattern",
                "Uses queue data structure",
            ],
        },
        "dfs": {
            "name": "Depth-First Search (DFS)",
            "description": "Explores as far as possible along each branch before backtracking",
            "time_complexity": "O(V + E)",
            "space_complexity": "O(V)",
            "uses_heuristic": False,
            "optimal": False,
            "characteristics": [
                "Explores deep into the graph before backtracking",
                "Not optimal - may not find shortest path",
                "Lower memory usage than BFS",
                "Faster initial exploration but longer paths",
                "Uses stack data structure (recursive or explicit)",
            ],
        },
    }

    @staticmethod
    def generate_text_report():
        """Generate a formatted text report"""
        report = []
        report.append("=" * 80)
        report.append("PAC-MAN GAME - ALGORITHM ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Project Overview
        report.append("PROJECT OVERVIEW")
        report.append("-" * 80)
        report.append(
            "This Pac-Man game implements multiple pathfinding algorithms for ghost AI"
        )
        report.append("Each ghost uses a different algorithm to chase the player:\n")

        # Algorithm Implementations
        report.append("ALGORITHMS IMPLEMENTED")
        report.append("-" * 80)

        for algo_key in ["astar", "dijkstra", "bfs", "dfs"]:
            info = AlgorithmReport.ALGORITHM_DESCRIPTIONS[algo_key]
            report.append(f"\n{info['name'].upper()}")
            report.append(f"Description: {info['description']}")
            report.append(f"Time Complexity: {info['time_complexity']}")
            report.append(f"Space Complexity: {info['space_complexity']}")
            report.append(f"Optimal: {'Yes' if info['optimal'] else 'No'}")
            report.append(
                f"Uses Heuristic: {'Yes' if info['uses_heuristic'] else 'No'}"
            )
            report.append("Characteristics:")
            for char in info["characteristics"]:
                report.append(f"  • {char}")

        # Ghost Implementation
        report.append("\n\nGHOST IMPLEMENTATION")
        report.append("-" * 80)
        report.append("""
GHOSTS_CONFIG = [
    {
        "name": "A*",
        "algorithm": "astar",      # Uses A* algorithm
        "color": RED,
        "initial_tile": (9, 9),
        "speed": 0.062,
        "release_at": 0,
    },
    {
        "name": "BFS",
        "algorithm": "bfs",        # Uses BFS algorithm
        "color": GHOST_BLUE,
        "initial_tile": (10, 9),
        "speed": 0.055,
        "release_at": 20,
    },
    {
        "name": "DIJK",
        "algorithm": "dijkstra",   # Uses Dijkstra algorithm
        "color": GHOST_ORANGE,
        "initial_tile": (11, 9),
        "speed": 0.06,
        "release_at": 45,
    },
]

Note: DFS can be used by adding to GHOSTS_CONFIG with "algorithm": "dfs"
""")

        # Performance Metrics
        report.append("\nPERFORMANCE METRICS")
        report.append("-" * 80)

        metrics_data = global_metrics.get_all_summaries()

        if metrics_data:
            report.append("\nAlgorithm Performance Statistics:\n")
            for algo_name, metrics in metrics_data.items():
                report.append(f"{algo_name.upper()}")
                report.append(f"  Calls:                 {metrics['calls']}")
                report.append(f"  Successful Searches:   {metrics['successful_paths']}")
                report.append(f"  Failed Searches:       {metrics['failed_searches']}")
                report.append(f"  Avg Execution Time:    {metrics['avg_time']:.3f} ms")
                report.append(
                    f"  Avg Path Length:       {metrics['avg_path_length']:.1f} tiles"
                )
                report.append(
                    f"  Total Time:            {metrics['total_time']:.3f} ms"
                )
                report.append("")
        else:
            report.append(
                "No performance data collected yet. Run the game to generate metrics."
            )

        # Why Each Algorithm Was Chosen
        report.append("\nWHY THESE ALGORITHMS")
        report.append("-" * 80)
        report.append("""
A* (Ghost 1 - Red):
  • Most efficient for pathfinding with a known target
  • Uses heuristic to guide search toward player
  • Guarantees shortest path while being faster than Dijkstra
  • Released immediately to provide difficulty

BFS (Ghost 2 - Blue):
  • Good balance between simplicity and optimality
  • Explores all possibilities at same depth before going deeper
  • Finds optimal path on unweighted grids
  • Released after 20 pellets eaten

Dijkstra (Ghost 3 - Orange):
  • Finds shortest path from a source to all nodes
  • No heuristic, so more computationally intensive
  • Demonstrates difference between uninformed search
  • Released after 45 pellets eaten

DFS (Available for extension):
  • Demonstrates non-optimal pathfinding
  • Lower memory usage than BFS
  • Good for comparison to show why A* and Dijkstra are better
  • Can be toggled to show path quality differences
""")

        # Conclusion
        report.append("\nCONCLUSION")
        report.append("-" * 80)
        report.append("""
This Pac-Man implementation demonstrates practical application of four fundamental
graph search algorithms. Each algorithm has different trade-offs:

- A* provides optimal AND efficient pathfinding (best overall)
- Dijkstra provides optimal pathfinding without heuristics
- BFS provides optimal pathfinding with simple implementation  
- DFS provides non-optimal pathfinding with lowest memory usage

The game shows how algorithm choice affects AI behavior and game difficulty.
""")

        report.append("=" * 80)

        return "\n".join(report)

    @staticmethod
    def generate_csv_report():
        """Generate a CSV report of metrics"""
        report = []
        report.append(
            "Algorithm,Calls,Successful_Searches,Failed_Searches,Avg_Time_ms,Avg_Path_Length,Total_Time_ms,Avg_Nodes_Explored"
        )

        metrics_data = global_metrics.get_all_summaries()
        for algo_name, metrics in metrics_data.items():
            line = (
                f"{algo_name},"
                f"{metrics['calls']},"
                f"{metrics['successful_paths']},"
                f"{metrics['failed_searches']},"
                f"{metrics['avg_time']:.3f},"
                f"{metrics['avg_path_length']:.1f},"
                f"{metrics['total_time']:.3f},"
                f"{metrics.get('avg_nodes_explored', 0):.1f}"
            )
            report.append(line)

        return "\n".join(report)

    @staticmethod
    def save_report(filename="algorithm_report.txt"):
        """Save report to file"""
        report_content = AlgorithmReport.generate_text_report()
        with open(filename, "w") as f:
            f.write(report_content)
        return filename

    @staticmethod
    def print_report():
        """Print report to console"""
        print(AlgorithmReport.generate_text_report())
