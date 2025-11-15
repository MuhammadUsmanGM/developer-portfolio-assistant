import os
from typing import Optional

import google.generativeai as genai

from ..utils.logging import log_event


def content_generator(
    github_summary: dict,
    repo_activity: Optional[dict] = None,
    format_style: str = "LinkedIn",
    tone: str = "professional",
    include_hashtags: bool = True,
) -> dict:
    """
    Uses Gemini to generate rich content from GitHub data and repo activity.
    Args:
        github_summary (dict): Output from github_analyzer tool
        repo_activity (dict): Output from github_repo_activity tool
        format_style (str): "LinkedIn", "Blog", or "README"
        tone (str): "professional", "energetic", "casual", etc.
        include_hashtags (bool): Add hashtags if True
    Returns:
        dict: {'content': ...}
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        log_event("Gemini API key not found.")
        return {"error": "Gemini API key not found in environment variables."}

    try:
        genai.configure(api_key=api_key)
    except Exception as config_error:
        log_event(f"Failed to configure Gemini API: {str(config_error)}")
        return {"error": f"Failed to configure Gemini API: {str(config_error)}"}

    name = github_summary.get("name") or github_summary.get("login", "a developer")
    bio = github_summary.get("bio", "")
    repos_count = github_summary.get("public_repos", "N/A")
    followers = github_summary.get("followers", "N/A")
    url = github_summary.get("profile_url", "")

    system_prompt = (
        f"You are an AI writing assistant helping developers auto-generate portfolio content.\n"
        f"Format: {format_style}. Tone: {tone}."
    )
    hashtags = "#Python #OpenSource #AI " if include_hashtags else ""

    repo_section = ""
    if repo_activity and "repos" in repo_activity:
        repo_section += "Recent repository activity summary:\n"
        for repo in repo_activity["repos"]:
            repo_section += f"- {repo['repo_name']}: {repo['description']}\n"
            for commit in repo["commits"]:
                repo_section += (
                    f"   - Latest commit: '{commit['message']}' ({commit['date']})\n"
                )

    prompt = (
        f"{system_prompt}\n"
        f"Developer profile: Name: {name}. Bio: '{bio}'. GitHub: {url}. "
        f"Repositories: {repos_count}. Followers: {followers}.\n"
        f"{repo_section}\n"
        f"Write a post summarizing this developer's recent work and encourage engagement.\n"
    )
    if include_hashtags:
        prompt += f"Add relevant hashtags at the end: {hashtags}\n"

    log_event(
        f"Gemini generation for '{name}' [{format_style}/{tone}] with {repos_count} repos. Prompt preview: {prompt[:150]}..."
    )

    # Try multiple model names in order of preference
    # gemini-2.0-flash is the free tier model
    # gemini-1.5-flash requires pro account
    # gemini-pro is deprecated
    model_names = [
        "gemini-2.0-flash",  # Free tier model (try first)
        "gemini-2.0-flash-exp",  # Experimental variant
        "gemini-1.5-flash",  # Pro account model
        "gemini-1.5-pro",  # Pro account model
    ]

    last_error = None
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            log_event(f"Attempting to generate content with model: {model_name}")
            response = model.generate_content([prompt])
            content = response.text
            log_event(
                f"Gemini generation success for '{name}' using {model_name}. Output preview: {content[:150]}..."
            )
            return {"content": content}
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            log_event(
                f"Failed to generate with model {model_name}: {error_type}: {error_msg}"
            )
            last_error = e
            # If it's a model not found error, try next model
            if "not found" in error_msg.lower() or "404" in error_msg:
                continue
            # For other errors (quota, auth, etc.), don't try other models
            break

    # If we get here, all models failed
    error_msg = str(last_error) if last_error else "Unknown error"
    error_type = type(last_error).__name__ if last_error else "Exception"
    log_event(f"Gemini API error for '{name}': {error_type}: {error_msg}")

    # Provide more detailed error information
    detailed_error = f"Gemini API error ({error_type}): {error_msg}"
    if "API_KEY" in error_msg.upper() or "authentication" in error_msg.lower():
        detailed_error += " - Check your GOOGLE_API_KEY environment variable."
    elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
        detailed_error += " - API quota or rate limit exceeded."
    elif "model" in error_msg.lower() or "not found" in error_msg.lower():
        detailed_error += " - None of the available models worked. Tried: " + ", ".join(
            model_names
        )
    return {"error": detailed_error}
