
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def review_code_diff(diff: str) -> dict:
    """Review a code diff and return structured findings."""

    if not diff or not diff.strip():
        return {
            "finding_count": 0,
            "findings": [],
            "summary": "No code diff was provided for review.",
        }

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Check your .env file."
        )

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="""
You are a senior software engineer reviewing GitHub pull requests.

Identify only actionable bugs, logic errors, security issues,
and maintainability problems that are supported by the diff.

Return valid JSON only, using this exact structure:
{
  "summary": "Short review summary",
  "finding_count": 0,
  "findings": [
    {
      "severity": "HIGH | MEDIUM | LOW",
      "file": "File path from the diff",
      "line": null,
      "issue": "Short issue title",
      "evidence": "Relevant code from the diff",
      "why_it_matters": "Practical impact",
      "suggested_fix": "Actionable fix"
    }
  ]
}

Rules:
- Use only HIGH, MEDIUM, or LOW for severity.
- Use a line number only if it can be determined reliably; otherwise use null.
- Do not invent file names, line numbers, or evidence.
- Do not report speculative issues.
- If no meaningful issues are found, return an empty findings array
  and explain that in the summary.
- finding_count must equal the number of findings.
""",
        input=f"Review this GitHub pull request diff:\n\n{diff}",
    )

    result_text = response.output_text

    try:
        result = json.loads(result_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"The AI returned invalid JSON: {result_text}"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError("The AI response must be a JSON object.")

    findings = result.get("findings")
    if not isinstance(findings, list):
        raise ValueError("The AI response must contain a findings list.")

    result["finding_count"] = len(findings)
    result.setdefault("summary", "Review completed.")

    return result


if __name__ == "__main__":
    sample_diff = """
File: example.py
Status: modified
Diff:
+def calculate_average(total, count):
+    return total / count
"""

    try:
        result = review_code_diff(sample_diff)
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print(f"Review failed: {type(exc).__name__}: {exc}")
