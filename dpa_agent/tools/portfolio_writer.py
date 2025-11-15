from ..utils.logging import log_event


def portfolio_writer(content: str, filename: str = "portfolio_entry.md") -> dict:
    """
    Saves generated content to a markdown file.
    Args:
        content (str): Content to write
        filename (str): Output filename (default: portfolio_entry.md)
    Returns:
        dict: Writing result
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        log_event(f"Portfolio entry saved to {filename} (success).")
        return {"status": "success", "file": filename}
    except Exception as e:
        log_event(f"Portfolio entry save failed for {filename}: {str(e)}")
        return {"status": "error", "reason": str(e)}
