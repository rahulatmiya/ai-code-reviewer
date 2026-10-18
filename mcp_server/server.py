
import os
import sys
import logging
from pathlib import Path

# --------------------------------------------------
# 1. Configure project path and environment
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from github import Auth, Github
from mcp.server.mcpserver import MCPServer
from reviewer.ai_reviewer import review_code_diff

load_dotenv(PROJECT_ROOT / ".env")

logging.basicConfig(
    stream=sys.stderr,
    level=logging.ERROR,
)

server = MCPServer("ai-code-reviewer")


# --------------------------------------------------
# 2. GitHub connection helper
# --------------------------------------------------

def get_github_repository():
    """Create a GitHub connection and return the repository."""
    token = os.getenv("GITHUB_TOKEN")
    repository_name = os.getenv("GITHUB_REPOSITORY")

    if not token or not repository_name:
        raise ValueError(
            "GITHUB_TOKEN or GITHUB_REPOSITORY is missing from .env."
        )

    github = Github(auth=Auth.Token(token))

    try:
        repo = github.get_repo(repository_name)
        return github, repo
    except Exception:
        github.close()
        raise


# --------------------------------------------------
# 3. MCP tool: Pull request details
# --------------------------------------------------

@server.tool()
def get_pull_request_details(pr_number: int) -> dict:
    """Get the title, state, description, URL, and branches of a PR."""
    github, repo = get_github_repository()

    try:
        pr = repo.get_pull(pr_number)

        return {
            "number": pr.number,
            "title": pr.title,
            "state": pr.state,
            "body": pr.body or "",
            "url": pr.html_url,
            "head_branch": pr.head.ref,
            "base_branch": pr.base.ref,
        }

    except Exception as exc:
        logging.exception("GitHub pull request lookup failed")
        return {"error": f"{type(exc).__name__}: {exc}"}

    finally:
        github.close()


# --------------------------------------------------
# 4. MCP tool: Pull request diff
# --------------------------------------------------

@server.tool()
def get_pull_request_diff(pr_number: int) -> str:
    """Retrieve changed files and code diffs from a GitHub PR."""
    github, repo = get_github_repository()

    try:
        pr = repo.get_pull(pr_number)
        diff_parts = []

        for file in pr.get_files():
            patch = file.patch or "(Diff unavailable for this file.)"

            diff_parts.append(
                f"File: {file.filename}\n"
                f"Status: {file.status}\n"
                f"Diff:\n{patch}"
            )

        return "\n\n".join(diff_parts) or "No changed files found."

    finally:
        github.close()


# --------------------------------------------------
# 5. MCP tool: Basic rule-based review
# --------------------------------------------------

@server.tool()
def analyze_pull_request_diff(pr_number: int) -> dict:
    """Run basic static checks against a pull request diff."""
    diff = get_pull_request_diff(pr_number)
    findings = []

    for line_number, line in enumerate(diff.splitlines(), start=1):
        if not line.startswith("+") or line.startswith("+++"):
            continue

        code = line[1:]

        if "TODO" in code:
            findings.append({
                "severity": "LOW",
                "finding": "TODO comment found in added code",
                "line": line_number,
                "suggestion": "Confirm the TODO is tracked and intentional.",
            })

        if "console.log(" in code:
            findings.append({
                "severity": "LOW",
                "finding": "Debug logging found in added code",
                "line": line_number,
                "suggestion": "Remove unnecessary debug logging.",
            })

        if "password" in code.lower() and "=" in code:
            findings.append({
                "severity": "HIGH",
                "finding": "Possible hard-coded password assignment",
                "line": line_number,
                "suggestion": (
                    "Use a secure secret store or environment variable."
                ),
            })

    return {
        "pull_request": pr_number,
        "analysis_type": "basic_static_checks",
        "finding_count": len(findings),
        "findings": findings,
        "note": "These are heuristic checks, not a full AI review.",
    }


# --------------------------------------------------
# 6. MCP tool: AI-powered code review
# --------------------------------------------------

@server.tool()
def ai_review_pull_request(pr_number: int) -> dict:
    """Use OpenAI to review a PR for bugs, logic errors, and code quality."""

    # Fetch the actual GitHub diff.
    diff = get_pull_request_diff(pr_number)

    if not diff or diff == "No changed files found.":
        return {
            "pull_request": pr_number,
            "status": "skipped",
            "message": "No code changes found to review.",
        }

    # This call makes a real OpenAI API request.
    review = review_code_diff(diff)

    return {
        "pull_request": pr_number,
        "status": "completed",
        "review": review,
    }


# --------------------------------------------------
# 7. Start MCP server
# --------------------------------------------------

if __name__ == "__main__":
    server.run(transport="stdio")
