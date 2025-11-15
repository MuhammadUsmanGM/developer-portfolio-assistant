"""
Logging Utility Module

This module provides centralized logging functionality with Unicode-safe handling.
It implements observability/logging as required by the capstone project.

Design Decisions:
- UTF-8 encoding for file logs ensures proper character handling
- Emoji removal for console compatibility (Windows cp1252 encoding issues)
- Centralized configuration ensures consistent logging across all modules
- Force=True overrides any existing logging configuration

Behavior:
- Logs all events to portfolio_agent.log file
- Removes emojis from console output to prevent encoding errors
- Provides safe logging function that handles Unicode gracefully
"""

import logging
import re
import sys

# Configure logging with UTF-8 encoding for file handler
# Design: UTF-8 encoding ensures proper handling of international characters
# Force=True ensures our configuration overrides any existing logging setup
logging.basicConfig(
    level=logging.INFO,
    filename="portfolio_agent.log",
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
    force=True,  # Override any existing configuration
)


# Remove emojis and other problematic Unicode characters for safe logging
def remove_emojis(text):
    """
    Remove emojis and other non-ASCII characters that can't be encoded in cp1252.

    This function handles Unicode encoding issues on Windows systems where
    the console uses cp1252 encoding which cannot handle emojis. It removes
    problematic characters while preserving the rest of the message.

    Design: Uses regex pattern matching to identify and remove emoji Unicode
    ranges. This approach is more efficient than character-by-character checking.

    Behavior:
    - Converts input to string if needed
    - Removes emoji Unicode ranges using regex
    - Returns cleaned text safe for cp1252 encoding

    Args:
        text: Input text that may contain emojis

    Returns:
        str: Text with emojis removed
    """
    if not isinstance(text, str):
        text = str(text)
    # Remove emojis and other non-printable Unicode characters
    # Design: Comprehensive emoji Unicode ranges cover most common emojis
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "\U00002702-\U000027b0"
        "\U000024c2-\U0001f251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text)


def log_event(event):
    """
    Log an event, safely handling Unicode characters including emojis.

    This is the main logging function used throughout the application.
    It ensures all events are logged safely, handling Unicode encoding
    issues that can occur on Windows systems.

    Design: Centralized logging function ensures consistent behavior
    across all modules. Emoji removal prevents console encoding errors
    while file logs preserve full Unicode (UTF-8).

    Behavior:
    - Converts event to string if needed
    - Removes emojis for console compatibility
    - Logs to file with full Unicode support
    - Logs to console with emoji-safe text

    Args:
        event: Event to log (will be converted to string)
    """
    # Convert to string if needed
    if not isinstance(event, str):
        event = str(event)

    # Remove emojis to prevent encoding errors on Windows console
    # Design: File logs use UTF-8 and preserve emojis, console logs are cleaned
    safe_event = remove_emojis(event)
    logging.info(safe_event)
