"""
Portfolio Update Orchestration Tool

This module provides the main workflow orchestration tool that coordinates
the complete portfolio update process. It implements a sequential agent pattern
by chaining multiple tools together.

Design Decisions:
- Sequential workflow: GitHub analysis -> Content generation -> File writing
- Error handling at each step prevents cascading failures
- Integrates with memory bank to persist updates
- Uses evaluation system to track performance

Behavior:
- Executes the complete portfolio update workflow
- Saves results to persistent memory
- Returns comprehensive results including all intermediate steps
"""

import time

from ..evaluation import get_evaluator
from ..memory import memory_bank
from ..utils.logging import log_event
from .content_generator import content_generator
from .github_analyzer import github_analyzer
from .portfolio_writer import portfolio_writer


def portfolio_update(username: str) -> dict:
    """
    Orchestrate the complete portfolio update workflow.

    This tool implements a sequential agent pattern by chaining multiple
    specialized tools together. It coordinates GitHub analysis, content generation,
    and file writing to complete a full portfolio update.

    Design: Sequential workflow ensures data flows correctly between steps.
    Each step validates its output before proceeding to the next, preventing
    cascading failures and providing clear error messages.

    Behavior:
    1. Analyzes GitHub profile and repositories
    2. Generates portfolio content using Gemini
    3. Writes content to markdown file
    4. Saves update to persistent memory
    5. Records metrics for evaluation

    Args:
        username (str): GitHub username to update portfolio for

    Returns:
        dict: Complete workflow results including all intermediate steps
    """
    start_time = time.time()
    log_event(f"Running portfolio_update for username: {username}")

    # Step 1: Analyze GitHub profile and repositories
    # Design: First step gathers all necessary data for content generation
    summary = github_analyzer(username)
    if "error" in summary:
        log_event(f"GitHub analysis failed for {username}: {summary['error']}")
        # Record failure for evaluation
        evaluator = get_evaluator(memory_bank)
        evaluator.record_operation("github_analyzer", False, time.time() - start_time)
        return {"error": f"GitHub analysis failed: {summary['error']}"}
    log_event(f"GitHub analysis succeeded for {username}")

    # Record success for evaluation
    evaluator = get_evaluator(memory_bank)
    evaluator.record_operation("github_analyzer", True, time.time() - start_time)

    # Step 2: Generate portfolio content using Gemini
    # Design: Content generation depends on successful GitHub analysis
    content_start = time.time()
    post = content_generator(summary)
    if "error" in post:
        log_event(f"Content generation failed for {username}: {post['error']}")
        evaluator.record_operation(
            "content_generator", False, time.time() - content_start
        )
        return {"error": f"Content generation failed: {post['error']}"}
    log_event(f"Content generation succeeded for {username}")

    # Evaluate content quality
    content = post.get("content", "") or post.get("linkedin_post", "")
    if content:
        quality_metrics = evaluator.evaluate_content_quality(content)
        log_event(f"Content quality score: {quality_metrics['score']}/100")
        evaluator.record_operation(
            "content_generator", True, time.time() - content_start
        )

    # Step 3: Write content to markdown file
    # Design: File writing is the final step, only proceeds if content was generated
    if not content:
        log_event(f"No content produced for {username}!")
        return {"error": "No content available for portfolio writing."}

    write_start = time.time()
    file_result = portfolio_writer(content)
    log_event(f"portfolio_writer result for {username}: {file_result}")

    # Record file writing operation
    write_success = file_result.get("status") == "success"
    evaluator.record_operation(
        "portfolio_writer", write_success, time.time() - write_start
    )

    # Save to persistent memory
    # Design: Memory persistence allows agent to recall past updates
    if write_success and content:
        memory_bank.save(
            username=username,
            post=content,
            meta={
                "github_summary": summary,
                "file_result": file_result,
                "quality_score": quality_metrics.get("score", 0) if content else 0,
            },
        )
        log_event(f"Portfolio update saved to memory for {username}")

    total_time = time.time() - start_time
    log_event(f"Portfolio update completed for {username} in {total_time:.2f} seconds")

    return {
        "github_summary": summary,
        "generated_post": post,
        "file_result": file_result,
        "execution_time": round(total_time, 2),
    }
