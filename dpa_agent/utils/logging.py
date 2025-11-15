import logging
import re
import sys

# Configure logging with UTF-8 encoding for file handler
logging.basicConfig(
    level=logging.INFO,
    filename="portfolio_agent.log",
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
    force=True,  # Override any existing configuration
)


# Remove emojis and other problematic Unicode characters for safe logging
def remove_emojis(text):
    """Remove emojis and other non-ASCII characters that can't be encoded in cp1252"""
    if not isinstance(text, str):
        text = str(text)
    # Remove emojis and other non-printable Unicode characters
    # Keep ASCII and common Latin-1 characters
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
    """Log an event, safely handling Unicode characters including emojis"""
    # Convert to string if needed
    if not isinstance(event, str):
        event = str(event)

    # Remove emojis to prevent encoding errors on Windows console
    safe_event = remove_emojis(event)
    logging.info(safe_event)
