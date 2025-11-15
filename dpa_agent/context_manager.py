"""
Context Engineering and Compaction

This module provides context management and compaction strategies for managing
LLM context windows. It implements context engineering as required by the capstone project.

Design Decisions:
- Token-based context tracking for accurate window management
- Multiple compaction strategies (summarization, truncation, importance-based)
- Context history for maintaining conversation continuity
- Configurable context window sizes per model

Behavior:
- Tracks context usage and token counts
- Compacts context when approaching limits
- Maintains important information while removing redundancy
- Supports different compaction strategies
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .utils.logging import log_event


class ContextManager:
    """
    Manages LLM context windows with compaction strategies.

    This class implements context engineering as required by the capstone project.
    It tracks context usage, manages context windows, and provides compaction
    strategies to stay within token limits.

    Attributes:
        max_tokens (int): Maximum tokens allowed in context
        current_tokens (int): Current token count
        context_history (list): History of context entries
        compaction_strategy (str): Current compaction strategy
    """

    def __init__(
        self, max_tokens: int = 32000, compaction_strategy: str = "importance"
    ):
        """
        Initialize the context manager.

        Args:
            max_tokens (int): Maximum tokens in context window
            compaction_strategy (str): Strategy to use ("importance", "summarize", "truncate")
        """
        self.max_tokens = max_tokens
        self.current_tokens = 0
        self.context_history: List[Dict[str, Any]] = []
        self.compaction_strategy = compaction_strategy
        self.important_entries: set = set()  # Track important entries to preserve

    def add_context(
        self,
        content: str,
        role: str = "user",
        importance: int = 1,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """
        Add content to the context.

        Behavior: Adds content to context history. If adding would exceed
        the token limit, compacts the context first.

        Args:
            content (str): Content to add
            role (str): Role of the content (user, assistant, system)
            importance (int): Importance level (1-10, higher = more important)
            metadata (dict, optional): Additional metadata

        Returns:
            bool: True if added successfully, False if compaction failed
        """
        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = len(content) // 4

        # Check if we need to compact
        if self.current_tokens + estimated_tokens > self.max_tokens:
            if not self.compact_context(estimated_tokens):
                log_event("Context compaction failed, cannot add new content")
                return False

        entry = {
            "content": content,
            "role": role,
            "importance": importance,
            "tokens": estimated_tokens,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        self.context_history.append(entry)
        self.current_tokens += estimated_tokens

        if importance >= 8:
            self.important_entries.add(len(self.context_history) - 1)

        log_event(
            f"Added context: {estimated_tokens} tokens, total: {self.current_tokens}/{self.max_tokens}"
        )
        return True

    def compact_context(self, required_tokens: int) -> bool:
        """
        Compact the context to make room for new content.

        Behavior: Uses the configured compaction strategy to reduce context
        size while preserving important information.

        Args:
            required_tokens (int): Number of tokens needed

        Returns:
            bool: True if compaction successful, False otherwise
        """
        if self.compaction_strategy == "importance":
            return self._compact_by_importance(required_tokens)
        elif self.compaction_strategy == "summarize":
            return self._compact_by_summarization(required_tokens)
        elif self.compaction_strategy == "truncate":
            return self._compact_by_truncation(required_tokens)
        else:
            log_event(f"Unknown compaction strategy: {self.compaction_strategy}")
            return False

    def _compact_by_importance(self, required_tokens: int) -> bool:
        """
        Compact by removing least important entries.

        Design: Preserves entries marked as important and removes others
        starting with the lowest importance scores.

        Args:
            required_tokens (int): Tokens needed

        Returns:
            bool: True if successful
        """
        # Sort by importance (lowest first), but preserve important entries
        entries_to_remove = []
        tokens_to_free = 0

        for i, entry in enumerate(self.context_history):
            if i not in self.important_entries and entry["importance"] < 5:
                entries_to_remove.append(i)
                tokens_to_free += entry["tokens"]
                if tokens_to_free >= required_tokens:
                    break

        # Remove entries in reverse order to maintain indices
        for i in reversed(entries_to_remove):
            self.current_tokens -= self.context_history[i]["tokens"]
            self.context_history.pop(i)
            # Update important_entries indices
            self.important_entries = {
                idx - 1 if idx > i else idx for idx in self.important_entries
            }

        log_event(f"Compacted context by importance: freed {tokens_to_free} tokens")
        return tokens_to_free >= required_tokens

    def _compact_by_summarization(self, required_tokens: int) -> bool:
        """
        Compact by summarizing older entries.

        Design: Summarizes older, less important entries into shorter versions.
        This preserves information while reducing token count.

        Args:
            required_tokens (int): Tokens needed

        Returns:
            bool: True if successful
        """
        # Summarize older entries (keep recent ones intact)
        tokens_freed = 0
        entries_to_summarize = len(self.context_history) // 2  # Summarize older half

        for i in range(entries_to_summarize):
            if i in self.important_entries:
                continue  # Don't summarize important entries

            entry = self.context_history[i]
            original_tokens = entry["tokens"]

            # Simple summarization: take first 100 chars + "..."
            if len(entry["content"]) > 100:
                entry["content"] = entry["content"][:100] + "... [summarized]"
                new_tokens = len(entry["content"]) // 4
                tokens_freed += original_tokens - new_tokens
                entry["tokens"] = new_tokens
                self.current_tokens -= original_tokens - new_tokens

            if tokens_freed >= required_tokens:
                break

        log_event(f"Compacted context by summarization: freed {tokens_freed} tokens")
        return tokens_freed >= required_tokens

    def _compact_by_truncation(self, required_tokens: int) -> bool:
        """
        Compact by truncating oldest entries.

        Design: Removes oldest entries first, preserving recent context.
        This is the simplest but most lossy strategy.

        Args:
            required_tokens (int): Tokens needed

        Returns:
            bool: True if successful
        """
        tokens_freed = 0
        entries_to_remove = []

        # Remove oldest entries (but preserve important ones)
        for i, entry in enumerate(self.context_history):
            if i not in self.important_entries:
                entries_to_remove.append(i)
                tokens_freed += entry["tokens"]
                if tokens_freed >= required_tokens:
                    break

        # Remove entries in reverse order
        for i in reversed(entries_to_remove):
            self.current_tokens -= self.context_history[i]["tokens"]
            self.context_history.pop(i)
            # Update important_entries indices
            self.important_entries = {
                idx - 1 if idx > i else idx for idx in self.important_entries
            }

        log_event(f"Compacted context by truncation: freed {tokens_freed} tokens")
        return tokens_freed >= required_tokens

    def get_context(self, format_for_llm: bool = True) -> List[Dict[str, Any]]:
        """
        Get the current context, optionally formatted for LLM.

        Args:
            format_for_llm (bool): Format as messages for LLM API

        Returns:
            list: Context entries or formatted messages
        """
        if format_for_llm:
            return [
                {"role": entry["role"], "content": entry["content"]}
                for entry in self.context_history
            ]
        return self.context_history

    def clear_context(self):
        """Clear all context."""
        self.context_history = []
        self.current_tokens = 0
        self.important_entries = set()
        log_event("Context cleared")

    def get_context_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current context.

        Returns:
            dict: Context statistics
        """
        return {
            "current_tokens": self.current_tokens,
            "max_tokens": self.max_tokens,
            "usage_percent": (self.current_tokens / self.max_tokens) * 100,
            "entries_count": len(self.context_history),
            "important_entries": len(self.important_entries),
            "compaction_strategy": self.compaction_strategy,
        }


# Global context manager instance
# Design: Singleton pattern ensures consistent context management
context_manager = ContextManager()
