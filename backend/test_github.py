import asyncio
from github_client import fetch_pr_files

async def main():
    pr_url = "https://github.com/fastapi/fastapi/pull/1"
    
    print(f"Fetching files for: {pr_url}\n")
    files = await fetch_pr_files(pr_url)
    
    print(f"Found {len(files)} files\n")
    for f in files:
        print(f"--- {f['filename']} ({f['status']}) ---")
        print(f['patch'][:300])
        print()

asyncio.run(main())