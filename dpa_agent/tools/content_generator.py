"""
Content Generation Tool

This module provides AI-powered content generation using Google Gemini.
It implements custom tools as required by the capstone project.

Design Decisions:
- Uses Google Generative AI (Gemini) for content generation
- Implements model fallback mechanism to support both free and pro API tiers
- Supports multiple content formats (LinkedIn, Blog, README)
- Configurable tone and style for different use cases

Behavior:
- Takes GitHub profile data and generates professional portfolio content
- Tries multiple Gemini models in order of preference
- Handles API errors gracefully with detailed error messages
- Logs all generation attempts for observability
"""

import os
from typing import Optional

import google.generativeai as genai

from ..context_manager import context_manager
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

    This tool implements AI-powered content generation as a custom tool for the agent.
    It transforms structured GitHub data into engaging portfolio content using
    Google's Gemini models.

    Design: Implements a model fallback mechanism that tries multiple Gemini models
    in order of preference. This ensures compatibility with both free-tier and
    pro-tier API keys, improving reliability and user experience.

    Behavior:
    - Validates API key from environment variables
    - Constructs a detailed prompt from GitHub data
    - Tries multiple Gemini models until one succeeds
    - Returns generated content or detailed error message

    Args:
        github_summary (dict): Output from github_analyzer tool containing profile data
        repo_activity (dict, optional): Output from github_repo_activity tool
        format_style (str): Content format - "LinkedIn", "Blog", or "README"
        tone (str): Writing tone - "professional", "energetic", "casual", etc.
        include_hashtags (bool): Whether to include hashtags in the content

    Returns:
        dict: Dictionary with 'content' key containing generated text, or 'error' key
    """
    # Retrieve API key from environment
    # Design: Environment variable approach keeps credentials secure
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        log_event("Gemini API key not found.")
        return {"error": "Gemini API key not found in environment variables."}

    try:
        # Configure Gemini API client
        # Design: Single configuration point for all model instances
        genai.configure(api_key=api_key)
    except Exception as config_error:
        log_event(f"Failed to configure Gemini API: {str(config_error)}")
        return {"error": f"Failed to configure Gemini API: {str(config_error)}"}

    # Extract relevant data from GitHub summary
    # Design: Use fallback values to handle missing data gracefully
    name = github_summary.get("name") or github_summary.get("login", "a developer")
    bio = github_summary.get("bio", "")
    repos_count = github_summary.get("public_repos", "N/A")
    followers = github_summary.get("followers", "N/A")
    url = github_summary.get("profile_url", "")

    # Construct system prompt with format and tone instructions
    # Design: Clear instructions help Gemini generate appropriate content
    system_prompt = (
        f"You are an AI writing assistant helping developers auto-generate portfolio content.\n"
        f"Format: {format_style}. Tone: {tone}."
    )
    hashtags = "#Python #OpenSource #AI " if include_hashtags else ""

    # Build repository activity section if repo_activity is provided
    # Design: Optional repo activity enriches content but isn't required
    repo_section = ""
    if repo_activity and "repos" in repo_activity:
        repo_section += "Recent repository activity summary:\n"
        for repo in repo_activity["repos"]:
            repo_section += f"- {repo['repo_name']}: {repo['description']}\n"
            for commit in repo["commits"]:
                repo_section += (
                    f"   - Latest commit: '{commit['message']}' ({commit['date']})\n"
                )

    # Construct the full prompt for Gemini
    # Design: Structured prompt with clear sections improves generation quality
    prompt = (
        f"{system_prompt}\n"
        f"Developer profile: Name: {name}. Bio: '{bio}'. GitHub: {url}. "
        f"Repositories: {repos_count}. Followers: {followers}.\n"
        f"{repo_section}\n"
        f"Write a post summarizing this developer's recent work and encourage engagement.\n"
    )
    if include_hashtags:
        prompt += f"Add relevant hashtags at the end: {hashtags}\n"

    # Context management: Add prompt to context
    # Design: Track context usage to manage token limits
    context_manager.add_context(
        prompt,
        role="user",
        importance=9,  # High importance - this is the main request
        metadata={"format_style": format_style, "tone": tone, "name": name},
    )

    log_event(
        f"Gemini generation for '{name}' [{format_style}/{tone}] with {repos_count} repos. Prompt preview: {prompt[:150]}..."
    )
    log_event(f"Context stats: {context_manager.get_context_stats()}")

    # Model fallback mechanism
    # Design: Try models in order of preference to support both free and pro API tiers
    # This improves reliability and user experience across different API key types
    model_names = [
        "gemini-2.0-flash",  # Free tier model (try first)
        "gemini-2.0-flash-exp",  # Experimental variant
        "gemini-1.5-flash",  # Pro account model
        "gemini-1.5-pro",  # Pro account model
    ]

    last_error = None
    # Try each model until one succeeds
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            log_event(f"Attempting to generate content with model: {model_name}")
            # Use context manager for prompt (if context is being used)
            # For now, use direct prompt, but context is tracked for future use
            response = model.generate_content([prompt])
            content = response.text

            # Add response to context
            context_manager.add_context(
                content,
                role="assistant",
                importance=8,  # High importance - generated content
                metadata={"model": model_name, "format_style": format_style},
            )

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
            # Design: Only retry on "not found" errors - other errors (quota, auth) are fatal
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
