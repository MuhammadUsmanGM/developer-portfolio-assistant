import requests

from ..utils.logging import log_event


def github_analyzer(username: str) -> dict:
    """
    Fetch basic public profile data from GitHub.
    Args:
        username (str): GitHub username
    Returns:
        dict: user summary or error
    """
    log_event(f"Attempting GitHub analysis for username: {username}")

    url = f"https://api.github.com/users/{username}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
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
            log_event(
                f"GitHub analysis API error for {username}: status {resp.status_code}"
            )
            return {"error": f"User '{username}' not found or API error."}
    except Exception as e:
        log_event(f"GitHub analysis exception for {username}: {str(e)}")
        return {"error": str(e)}


def github_repo_activity(username: str, top_n: int = 3) -> dict:
    """
    Fetch summary of a user's top N public GitHub repositories.
    Returns repo names, descriptions, and recent commit activity.
    """
    log_event(f"Fetching repo activity for username: {username} (top_n={top_n})")
    repos_url = (
        f"https://api.github.com/users/{username}/repos?sort=updated&type=public"
    )
    try:
        resp = requests.get(repos_url, timeout=10)
        if resp.status_code != 200:
            log_event(f"Repo fetch failed for {username}: status {resp.status_code}")
            return {"error": "Failed to fetch repos"}
        repos = resp.json()[:top_n]
        repo_summaries = []
        for repo in repos:
            repo_name = repo["name"]
            repo_desc = repo.get("description", "")
            commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
            commits_resp = requests.get(commits_url, timeout=10)
            commits = []
            if commits_resp.status_code == 200:
                commits = [
                    {
                        "message": c["commit"]["message"],
                        "date": c["commit"]["committer"]["date"],
                    }
                    for c in commits_resp.json()[:3]  # last 3 commits per repo
                ]
            repo_summaries.append(
                {"repo_name": repo_name, "description": repo_desc, "commits": commits}
            )
        log_event(f"Repo activity fetch complete for {username}: {repo_summaries}")
        return {"repos": repo_summaries}
    except Exception as e:
        log_event(f"Repo activity error for {username}: {str(e)}")
        return {"error": str(e)}
