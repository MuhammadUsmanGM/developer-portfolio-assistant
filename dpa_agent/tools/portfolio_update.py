from ..utils.logging import log_event
from .content_generator import content_generator
from .github_analyzer import github_analyzer
from .portfolio_writer import portfolio_writer


def portfolio_update(username: str) -> dict:
    log_event(f"Running portfolio_update for username: {username}")

    # Step 1: Analyze GitHub
    summary = github_analyzer(username)
    if "error" in summary:
        log_event(f"GitHub analysis failed for {username}: {summary['error']}")
        return {"error": f"GitHub analysis failed: {summary['error']}"}
    log_event(f"GitHub analysis succeeded for {username}")

    # Step 2: Generate content
    post = content_generator(summary)
    if "error" in post:
        log_event(f"Content generation failed for {username}: {post['error']}")
        return {"error": f"Content generation failed: {post['error']}"}
    log_event(f"Content generation succeeded for {username}")

    # Step 3: Write content to markdown
    content = post.get("content", "") or post.get("linkedin_post", "")
    if not content:
        log_event(f"No content produced for {username}!")
        return {"error": "No content available for portfolio writing."}
    file_result = portfolio_writer(content)
    log_event(f"portfolio_writer result for {username}: {file_result}")

    return {
        "github_summary": summary,
        "generated_post": post,
        "file_result": file_result,
    }
