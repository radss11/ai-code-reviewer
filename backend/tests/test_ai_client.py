import pytest
import json
from unittest.mock import patch, MagicMock
from ai_client import review_file


# --- Tests for review_file ---

@pytest.mark.asyncio
async def test_review_file_returns_valid_json():
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "filename": "main.py",
        "summary": "Adds input validation",
        "issues": [],
        "verdict": "approved"
    })

    with patch("ai_client.client") as mock_client:
        mock_client.models.generate_content.return_value = mock_response
        result = await review_file("main.py", "@@ -1 +1 @@\n+code")

    assert result["filename"] == "main.py"
    assert result["verdict"] == "approved"
    assert isinstance(result["issues"], list)


@pytest.mark.asyncio
async def test_review_file_handles_markdown_fences():
    mock_response = MagicMock()
    mock_response.text = "```json\n" + json.dumps({
        "filename": "main.py",
        "summary": "Test",
        "issues": [],
        "verdict": "approved"
    }) + "\n```"

    with patch("ai_client.client") as mock_client:
        mock_client.models.generate_content.return_value = mock_response
        result = await review_file("main.py", "@@ -1 +1 @@\n+code")

    assert result["verdict"] == "approved"


@pytest.mark.asyncio
async def test_review_file_handles_invalid_json():
    mock_response = MagicMock()
    mock_response.text = "This is not valid JSON at all"

    with patch("ai_client.client") as mock_client:
        mock_client.models.generate_content.return_value = mock_response
        result = await review_file("main.py", "@@ -1 +1 @@\n+code")

    assert result["filename"] == "main.py"
    assert result["summary"] == "Could not parse AI response"
    assert result["verdict"] == "needs_changes"


@pytest.mark.asyncio
async def test_review_file_retries_on_503():
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "filename": "main.py",
        "summary": "Test",
        "issues": [],
        "verdict": "approved"
    })

    with patch("ai_client.client") as mock_client:
        mock_client.models.generate_content.side_effect = [
            Exception("503 UNAVAILABLE"),
            mock_response
        ]
        result = await review_file("main.py", "@@ -1 +1 @@\n+code")

    assert result["verdict"] == "approved"