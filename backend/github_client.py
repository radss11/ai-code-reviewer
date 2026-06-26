import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


def parse_pr_url(pr_url: str):
    # e.g. https://github.com/owner/repo/pull/42
    parts = pr_url.rstrip("/").split("/")
    owner = parts[-4]
    repo = parts[-3]
    pr_number = parts[-1]
    return owner, repo, pr_number


async def fetch_pr_files(pr_url: str):
    owner, repo, pr_number = parse_pr_url(pr_url)
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=HEADERS)
        response.raise_for_status()
        files = response.json()
    return [
        {
            "filename": f["filename"],
            "patch": f.get("patch", ""),  # the diff
            "status": f["status"]         # added/modified/removed
        }
        for f in files
        if f.get("patch")  # skip binary files
    ]