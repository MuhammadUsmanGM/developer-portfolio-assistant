"""
Agent Evaluation Metrics

This module provides evaluation metrics for the Developer Portfolio Assistant.
It implements agent evaluation as required by the capstone project.

Design Decisions:
- Metrics tracking for success rates, content quality, and performance
- Evaluation data stored alongside memory for analysis
- Configurable evaluation criteria for different use cases

Behavior:
- Tracks success/failure rates for each tool
- Measures content quality metrics (length, completeness)
- Records performance metrics (execution time)
- Provides evaluation summaries for agent performance analysis
"""

import time
from datetime import datetime
from typing import Dict, List, Optional

from .memory import PersistentMemoryBank


class AgentEvaluator:
    """
    Evaluation system for agent performance and content quality.

    This class implements agent evaluation as required by the capstone project.
    It tracks metrics such as success rates, content quality, and execution times
    to assess agent performance and identify areas for improvement.

    Attributes:
        memory_bank (PersistentMemoryBank): Memory bank for storing evaluation data
        metrics (dict): In-memory metrics cache
    """

    def __init__(self, memory_bank: PersistentMemoryBank):
        """
        Initialize the evaluator.

        Args:
            memory_bank (PersistentMemoryBank): Memory bank for persistence
        """
        self.memory_bank = memory_bank
        self.metrics = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "tool_usage": {},  # Track usage per tool
            "content_quality": [],  # Track content quality metrics
            "performance": [],  # Track execution times
        }

    def record_operation(
        self,
        operation_type: str,
        success: bool,
        execution_time: Optional[float] = None,
        metadata: Optional[Dict] = None,
    ):
        """
        Record an agent operation for evaluation.

        Behavior: Tracks operation success/failure, execution time, and metadata.
        Updates metrics counters and stores detailed information for analysis.

        Args:
            operation_type (str): Type of operation (e.g., "github_analyzer", "content_generator")
            success (bool): Whether the operation succeeded
            execution_time (float, optional): Execution time in seconds
            metadata (dict, optional): Additional metadata about the operation
        """
        self.metrics["total_operations"] += 1

        if success:
            self.metrics["successful_operations"] += 1
        else:
            self.metrics["failed_operations"] += 1

        # Track tool usage
        if operation_type not in self.metrics["tool_usage"]:
            self.metrics["tool_usage"][operation_type] = {
                "total": 0,
                "success": 0,
                "failure": 0,
            }

        self.metrics["tool_usage"][operation_type]["total"] += 1
        if success:
            self.metrics["tool_usage"][operation_type]["success"] += 1
        else:
            self.metrics["tool_usage"][operation_type]["failure"] += 1

        # Track performance
        if execution_time is not None:
            self.metrics["performance"].append(
                {
                    "operation": operation_type,
                    "time": execution_time,
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def evaluate_content_quality(
        self, content: str, min_length: int = 100, max_length: int = 2000
    ) -> Dict[str, any]:
        """
        Evaluate the quality of generated content.

        Behavior: Analyzes content for quality metrics including length,
        completeness, and structure. Returns a quality score and metrics.

        Design: Uses simple heuristics for evaluation. In a production system,
        this could use more sophisticated NLP metrics or LLM-based evaluation.

        Args:
            content (str): Generated content to evaluate
            min_length (int): Minimum expected content length
            max_length (int): Maximum expected content length

        Returns:
            dict: Quality metrics including score, length, completeness
        """
        length = len(content)
        word_count = len(content.split())

        # Calculate quality score (0-100)
        # Length score: optimal range gets full points
        if min_length <= length <= max_length:
            length_score = 100
        elif length < min_length:
            length_score = (length / min_length) * 50  # Partial credit
        else:
            length_score = max(0, 100 - ((length - max_length) / max_length) * 50)

        # Completeness: check for key elements
        has_hashtags = "#" in content
        has_links = "http" in content or "github.com" in content
        has_engagement = any(
            word in content.lower() for word in ["check", "see", "view", "explore"]
        )

        completeness_score = 0
        if has_hashtags:
            completeness_score += 25
        if has_links:
            completeness_score += 25
        if has_engagement:
            completeness_score += 25
        if word_count > 50:  # Substantial content
            completeness_score += 25

        quality_score = (length_score * 0.5) + (completeness_score * 0.5)

        quality_metrics = {
            "score": round(quality_score, 2),
            "length": length,
            "word_count": word_count,
            "has_hashtags": has_hashtags,
            "has_links": has_links,
            "has_engagement": has_engagement,
            "timestamp": datetime.now().isoformat(),
        }

        self.metrics["content_quality"].append(quality_metrics)
        return quality_metrics

    def get_success_rate(self) -> float:
        """
        Calculate overall success rate.

        Returns:
            float: Success rate as a percentage (0-100)
        """
        if self.metrics["total_operations"] == 0:
            return 0.0
        return (
            self.metrics["successful_operations"] / self.metrics["total_operations"]
        ) * 100

    def get_tool_success_rate(self, tool_name: str) -> Optional[float]:
        """
        Get success rate for a specific tool.

        Args:
            tool_name (str): Name of the tool

        Returns:
            float: Success rate for the tool, or None if tool not found
        """
        if tool_name not in self.metrics["tool_usage"]:
            return None

        tool_metrics = self.metrics["tool_usage"][tool_name]
        if tool_metrics["total"] == 0:
            return 0.0

        return (tool_metrics["success"] / tool_metrics["total"]) * 100

    def get_average_execution_time(
        self, operation_type: Optional[str] = None
    ) -> Optional[float]:
        """
        Get average execution time for operations.

        Args:
            operation_type (str, optional): Filter by operation type

        Returns:
            float: Average execution time in seconds, or None if no data
        """
        if not self.metrics["performance"]:
            return None

        times = [
            p["time"]
            for p in self.metrics["performance"]
            if operation_type is None or p["operation"] == operation_type
        ]

        if not times:
            return None

        return sum(times) / len(times)

    def get_evaluation_summary(self) -> Dict[str, any]:
        """
        Get a comprehensive evaluation summary.

        Returns:
            dict: Summary of all evaluation metrics
        """
        avg_content_quality = 0.0
        if self.metrics["content_quality"]:
            avg_content_quality = sum(
                q["score"] for q in self.metrics["content_quality"]
            ) / len(self.metrics["content_quality"])

        return {
            "overall_success_rate": round(self.get_success_rate(), 2),
            "total_operations": self.metrics["total_operations"],
            "successful_operations": self.metrics["successful_operations"],
            "failed_operations": self.metrics["failed_operations"],
            "average_content_quality": round(avg_content_quality, 2),
            "tool_success_rates": {
                tool: round(self.get_tool_success_rate(tool), 2)
                for tool in self.metrics["tool_usage"].keys()
            },
            "average_execution_time": round(
                self.get_average_execution_time() or 0.0, 2
            ),
            "timestamp": datetime.now().isoformat(),
        }


# Global evaluator instance
# Design: Singleton pattern ensures consistent evaluation across all agents
evaluator: Optional[AgentEvaluator] = None


def get_evaluator(memory_bank: PersistentMemoryBank) -> AgentEvaluator:
    """
    Get or create the global evaluator instance.

    Args:
        memory_bank (PersistentMemoryBank): Memory bank instance

    Returns:
        AgentEvaluator: Global evaluator instance
    """
    global evaluator
    if evaluator is None:
        evaluator = AgentEvaluator(memory_bank)
    return evaluator
