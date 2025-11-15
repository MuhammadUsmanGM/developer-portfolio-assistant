"""
GitHub Analysis Tools

This module provides tools for analyzing GitHub profiles and repositories.
It implements custom tools as required by the capstone project.

Design Decisions:
- Uses GitHub REST API for data fetching (no authentication required for public data)
- Timeout handling prevents hanging requests
- Structured error handling with detailed error messages
- Logging integration for observability

Behavior:
- Fetches public profile data from GitHub API
- Analyzes repository activity and commit history
- Returns structured data for content generation
"""

import requests

from ..utils.logging import log_event


def github_analyzer(username: str) -> dict:
    """
    Fetch basic public profile data from GitHub.

    This tool implements GitHub profile analysis as a custom tool for the agent.
    It fetches public profile information including name, bio, repository count,
    and follower count from the GitHub REST API.

    Design: Uses GitHub's public API endpoint which doesn't require authentication
    for public profile data. Timeout is set to 10 seconds to prevent hanging requests.

    Behavior:
    - Makes HTTP GET request to GitHub API
    - Extracts relevant profile fields
    - Returns structured dictionary with profile data
    - Handles errors gracefully with detailed error messages

    Args:
        username (str): GitHub username to analyze

    Returns:
        dict: Dictionary containing profile data, or error dictionary if failed
    """
    log_event(f"Attempting GitHub analysis for username: {username}")

    # GitHub REST API endpoint for user profile
    # Design: Using public API endpoint - no authentication needed for public profiles
    url = f"https://api.github.com/users/{username}"
    try:
        # Timeout prevents hanging if GitHub API is slow or unresponsive
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # Extract only relevant fields for portfolio generation
            # Design: Selective field extraction keeps data structure clean and focused
            result = {
                "login": data.get("login"),
                "name": data.get("name"),
                "public_repos": data.get("public_repos"),
                "followers": data.get("followers"),
                "bio": data.get("bio"),
                "profile_url": data.get("html_url"),
            }
            log_event(f"GitHub analysis successful for {username}: {result}")
            return result
        else:
            # Handle API errors (404 for not found, 403 for rate limits, etc.)
            log_event(
                f"GitHub analysis API error for {username}: status {resp.status_code}"
            )
            return {"error": f"User '{username}' not found or API error."}
    except Exception as e:
        # Catch network errors, timeout errors, and other exceptions
        log_event(f"GitHub analysis exception for {username}: {str(e)}")
        return {"error": str(e)}


def github_repo_activity(username: str, top_n: int = 3) -> dict:
    """
    Fetch summary of a user's top N public GitHub repositories.

    This tool analyzes repository activity by fetching the most recently updated
    repositories and their recent commit history. This provides context for
    generating portfolio content that highlights recent work.

    Design: Fetches repositories sorted by update date, then fetches commit history
    for each repository. Limits to top N repositories and last 3 commits per repo
    to keep data manageable and API calls reasonable.

    Behavior:
    - Fetches list of public repositories sorted by last update
    - For each repo, fetches recent commit history
    - Returns structured data with repo names, descriptions, and commits
    - Handles missing descriptions and commit fetch failures gracefully

    Args:
        username (str): GitHub username
        top_n (int): Number of top repositories to analyze (default: 3)

    Returns:
        dict: Dictionary containing repository summaries with commit history
    """
    log_event(f"Fetching repo activity for username: {username} (top_n={top_n})")

    # GitHub API endpoint for user repositories
    # Design: Sort by 'updated' to get most recently active repositories
    repos_url = (
        f"https://api.github.com/users/{username}/repos?sort=updated&type=public"
    )
    try:
        resp = requests.get(repos_url, timeout=10)
        if resp.status_code != 200:
            log_event(f"Repo fetch failed for {username}: status {resp.status_code}")
            return {"error": "Failed to fetch repos"}

        # Get top N most recently updated repositories
        repos = resp.json()[:top_n]
        repo_summaries = []

        # Analyze each repository
        for repo in repos:
            repo_name = repo["name"]
            repo_desc = repo.get(
                "description", ""
            )  # Some repos may not have descriptions

            # Fetch recent commits for this repository
            # Design: Separate API call per repo to get commit history
            commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
            commits_resp = requests.get(commits_url, timeout=10)
            commits = []

            if commits_resp.status_code == 200:
                # Extract last 3 commits with message and date
                # Design: Limit to 3 commits to keep data focused and manageable
                commits = [
                    {
                        "message": c["commit"]["message"],
                        "date": c["commit"]["committer"]["date"],
                    }
                    for c in commits_resp.json()[:3]
                ]

            # Build repository summary
            repo_summaries.append(
                {"repo_name": repo_name, "description": repo_desc, "commits": commits}
            )

        log_event(f"Repo activity fetch complete for {username}: {repo_summaries}")
        return {"repos": repo_summaries}
    except Exception as e:
        log_event(f"Repo activity error for {username}: {str(e)}")
        return {"error": str(e)}
