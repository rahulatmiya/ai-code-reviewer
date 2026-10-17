
# AI Code Reviewer

An AI-powered Python code reviewer that automatically analyzes GitHub Pull Requests and posts actionable feedback.

## Features

- Automatically reviews PRs when opened, updated, or reopened.
- Identifies potential bugs, security issues, performance problems, and code-quality concerns.
- Assigns severity levels to findings.
- Suggests improvements for reported issues.
- Posts review summaries and findings as GitHub PR comments.
- Includes automated tests that run without calling the AI API.

## Technology Stack

- Python 3.12
- OpenAI API
- PyGithub
- GitHub Actions
- Pytest

## Project Structure

```text
ai-code-reviewer/
├── .github/
│   └── workflows/
│       └── ai-review.yml
├── reviewer/
│   ├── __init__.py
│   └── review_pr.py
├── tests/
│   └── test_review_pr.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Local Setup

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Run the automated tests:

   ```bash
   python -m pytest -v
   ```

## GitHub Actions Configuration

Add an `OPENAI_API_KEY` repository secret under:

**Settings → Secrets and variables → Actions → New repository secret**

The workflow uses GitHub's built-in `GITHUB_TOKEN` to access the pull request and publish a comment.

Never commit API keys or other secrets to the repository.

## Current Limitations

- The first version reviews text-based diffs only.
- Large diffs are truncated to a fixed character limit.
- AI findings should be reviewed by a human before changes are made.
- Pull requests from forks may not have access to repository secrets.

## Future Improvements

- Inline comments on specific changed lines.
- Better handling of large pull requests.
- Structured AI responses and stronger validation.
- Additional unit tests and CI checks.
- Optional Model Context Protocol (MCP) integration.
