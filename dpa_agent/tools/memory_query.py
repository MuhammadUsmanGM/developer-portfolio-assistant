"""
Memory Query Tool

This module provides a tool for querying persistent memory history.
It implements a custom tool as required by the capstone project.

Design Decisions:
- Uses shared memory_bank instance for consistency
- Supports filtering by username for user-specific queries
- Returns structured data for easy consumption by agents

Behavior:
- Queries persistent memory for past portfolio updates
- Can filter by username or return all history
- Returns structured dictionary with history data
"""

from typing import Optional

from ..memory import memory_bank

# Use shared memory bank instance
# Design: Singleton pattern ensures all tools access the same memory


def get_history(username: Optional[str] = None) -> dict:
    """
    Get persistent memory history for a username or all users.

    This tool implements memory querying as a custom tool for the agent.
    It allows agents to recall past portfolio updates, enabling
    context-aware interactions and avoiding duplicate work.

    Design: Optional username parameter allows for both user-specific
    and global queries. This flexibility supports different use cases
    from personal portfolio management to admin/debugging.

    Behavior:
    - If username provided: returns history for that user only
    - If username is None: returns all history (for admin/debugging)
    - Returns structured dictionary for easy consumption

    Args:
        username (str, optional): Filter history by this username

    Returns:
        dict: Dictionary with 'history' key containing list of entries
    """
    history = memory_bank.get_history(username)
    return {"history": history}
