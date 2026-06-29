import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from github_client import parse_pr_url, fetch_pr_files


# --- Tests for parse_pr_url ---

def test_parse_pr_url_standard():
    owner, repo, pr_number = parse_pr_url("https://github.com/fastapi/fastapi/pull/1")
    assert owner == "fastapi"
    assert repo == "fastapi"
    assert pr_number == "1"


def test_parse_pr_url_different_repo():
    owner, repo, pr_number = parse_pr_url("https://github.com/vercel/next.js/pull/42")
    assert owner == "vercel"
    assert repo == "next.js"
    assert pr_number == "42"


def test_parse_pr_url_trailing_slash():
    owner, repo, pr_number = parse_pr_url("https://github.com/owner/repo/pull/99/")
    assert owner == "owner"
    assert repo == "repo"
    assert pr_number == "99"


# --- Tests for fetch_pr_files ---

@pytest.mark.asyncio
async def test_fetch_pr_files_returns_files():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"filename": "main.py", "patch": "@@ -1,3 +1,4 @@\n+new line", "status": "modified"},
        {"filename": "README.md", "patch": "@@ -1 +1,2 @@\n+docs", "status": "modified"},
    ]
    mock_response.raise_for_status = MagicMock()

    with patch("github_client.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        files = await fetch_pr_files("https://github.com/owner/repo/pull/1")

    assert len(files) == 2
    assert files[0]["filename"] == "main.py"
    assert files[1]["filename"] == "README.md"


@pytest.mark.asyncio
async def test_fetch_pr_files_skips_binary():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"filename": "image.png", "status": "added"},  # no patch = binary
        {"filename": "main.py", "patch": "@@ -1 +1 @@\n+code", "status": "modified"},
    ]
    mock_response.raise_for_status = MagicMock()

    with patch("github_client.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        files = await fetch_pr_files("https://github.com/owner/repo/pull/1")

    assert len(files) == 1
    assert files[0]["filename"] == "main.py"