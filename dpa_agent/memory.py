"""
Persistent Memory Bank Implementation

This module provides long-term memory storage for the Developer Portfolio Assistant.
It implements a JSON-backed memory system that persists portfolio updates across sessions.

Design Decisions:
- JSON format chosen for human readability and easy debugging
- UTF-8 encoding ensures proper handling of international characters
- Lazy loading: memory is loaded once at initialization for performance
- Atomic writes: each save operation persists immediately to prevent data loss

Behavior:
- Automatically loads existing memory on initialization
- Saves entries with timestamps for chronological tracking
- Supports filtering by username for user-specific queries
- Gracefully handles file errors without crashing the application
"""

import datetime
import json
import os


class PersistentMemoryBank:
    """
    Long-term memory storage for portfolio updates.

    This class implements persistent memory as required by the capstone project.
    It stores all portfolio updates in a JSON file, allowing the agent to recall
    past activities and maintain context across sessions.

    Attributes:
        filename (str): Path to the JSON file storing memory entries
        entries (list): In-memory list of all stored entries
    """

    def __init__(self, filename="memory_bank.json"):
        """
        Initialize the memory bank and load existing entries.

        Design: Loads memory at initialization to ensure all agents have access
        to historical data immediately. This follows the singleton pattern used
        in agent.py where memory_bank is shared across all agents.

        Args:
            filename (str): Path to the JSON file for persistence
        """
        self.filename = filename
        self.entries = self._load_entries()

    def _load_entries(self):
        """
        Load entries from the JSON file.

        Behavior: Attempts to read and parse the JSON file. If the file doesn't
        exist or is corrupted, returns an empty list. This graceful degradation
        ensures the agent can start even if memory file is missing.

        Returns:
            list: List of memory entries, or empty list if file doesn't exist
        """
        if os.path.isfile(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Graceful degradation: if file is corrupted, start fresh
                # This prevents the agent from crashing due to bad memory data
                return []
        else:
            return []

    def save(self, username, post, meta=None):
        """
        Save a new portfolio update to memory.

        This method creates a memory entry with timestamp and persists it immediately.
        The immediate persistence ensures data isn't lost if the application crashes.

        Design: Each entry includes username, post content, metadata, and timestamp.
        This structure allows for rich queries and filtering by various criteria.

        Args:
            username (str): GitHub username associated with this update
            post (str): The generated portfolio content
            meta (dict, optional): Additional metadata about the update

        Returns:
            dict: The saved entry with all fields including timestamp
        """
        entry = {
            "username": username,
            "post": post,
            "meta": meta or {},
            "timestamp": datetime.datetime.now().isoformat(),
        }
        self.entries.append(entry)
        self._persist()  # Immediate persistence for data safety
        return entry

    def _persist(self):
        """
        Write all entries to the JSON file.

        Behavior: Writes the entire entries list to disk. This approach ensures
        consistency - either all entries are saved or none (atomic operation).
        Uses pretty-printing (indent=2) for human readability during debugging.

        Error Handling: Catches and logs errors without raising exceptions.
        This prevents memory save failures from crashing the agent workflow.
        """
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2)
        except Exception as e:
            # Log error but don't crash - memory persistence is important but not critical
            print(f"Error saving memory: {str(e)}")

    def get_history(self, username=None):
        """
        Retrieve memory entries, optionally filtered by username.

        This method supports the get_history tool used by agents to query past
        portfolio updates. Filtering by username allows for user-specific queries.

        Behavior:
        - If username is provided, returns only entries for that user
        - If username is None, returns all entries (for admin/debugging purposes)

        Args:
            username (str, optional): Filter entries by this username

        Returns:
            list: List of memory entries matching the filter criteria
        """
        if username:
            # Filter entries by username for user-specific queries
            return [e for e in self.entries if e["username"] == username]
        # Return all entries if no username filter specified
        return self.entries


# Create a singleton instance of the memory bank
# This ensures all modules share the same memory instance
# Design: Module-level singleton pattern for consistent memory access
memory_bank = PersistentMemoryBank()