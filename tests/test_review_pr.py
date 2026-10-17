
import json

import pytest

import reviewer.review_pr as review_pr


def test_review_diff_accepts_valid_response(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    expected = {
        "summary": "No major issues found.",
        "findings": [],
    }

    class FakeResponses:
        def create(self, **kwargs):
            class FakeResponse:
                output_text = json.dumps(expected)

            return FakeResponse()

    class FakeClient:
        responses = FakeResponses()

    monkeypatch.setattr(
        review_pr,
        "OpenAI",
        lambda api_key: FakeClient(),
    )

    result = review_pr.review_diff("Sample code diff")

    assert result == expected


def test_review_diff_rejects_invalid_severity(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    invalid_result = {
        "summary": "Review complete.",
        "findings": [
            {
                "severity": "URGENT",
                "file": "example.py",
                "issue": "Example issue",
                "suggestion": "Example fix",
            }
        ],
    }

    class FakeResponses:
        def create(self, **kwargs):
            class FakeResponse:
                output_text = json.dumps(invalid_result)

            return FakeResponse()

    class FakeClient:
        responses = FakeResponses()

    monkeypatch.setattr(
        review_pr,
        "OpenAI",
        lambda api_key: FakeClient(),
    )

    with pytest.raises(ValueError, match="Invalid finding severity"):
        review_pr.review_diff("Sample code diff")
