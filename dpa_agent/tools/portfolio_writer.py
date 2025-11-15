"""
Portfolio Writer Tool

This module provides file writing functionality for saving generated portfolio content.
It implements a custom tool as required by the capstone project.

Design Decisions:
- UTF-8 encoding ensures proper handling of international characters
- Default filename allows for easy customization
- Error handling prevents crashes from file system issues
- Logging integration for observability

Behavior:
- Writes content to markdown file with UTF-8 encoding
- Returns success/error status with details
- Logs all file operations for traceability
"""

from ..utils.logging import log_event


def portfolio_writer(content: str, filename: str = "portfolio_entry.md") -> dict:
    """
    Saves generated content to a markdown file.

    This tool implements file writing as a custom tool for the agent.
    It handles writing portfolio content to disk with proper encoding
    and error handling.

    Design: Uses UTF-8 encoding to support international characters and emojis.
    Default filename allows the tool to work out-of-the-box while still
    supporting customization.

    Behavior:
    - Opens file in write mode with UTF-8 encoding
    - Writes content to file
    - Returns success/error status
    - Logs operation for observability

    Args:
        content (str): Portfolio content to write to file
        filename (str): Output filename (default: portfolio_entry.md)

    Returns:
        dict: Dictionary with 'status' ('success' or 'error') and additional info
    """
    try:
        # Write content with UTF-8 encoding
        # Design: UTF-8 encoding ensures proper handling of international characters
        # and emojis that may appear in generated content
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        log_event(f"Portfolio entry saved to {filename} (success).")
        return {"status": "success", "file": filename}
    except Exception as e:
        # Handle file system errors gracefully
        # Design: Catch all exceptions to prevent file errors from crashing the agent
        log_event(f"Portfolio entry save failed for {filename}: {str(e)}")
        return {"status": "error", "reason": str(e)}
