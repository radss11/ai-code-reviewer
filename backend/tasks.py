from celery_app import celery
from github_client import fetch_pr_files
from ai_client import review_file
from database import save_review, init_db
import redis
import json
import os
import asyncio
import hashlib

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


def get_pr_id(pr_url: str) -> str:
    return hashlib.md5(pr_url.encode()).hexdigest()[:8]


@celery.task
def process_pr(pr_url: str):
    pr_id = get_pr_id(pr_url)
    r = redis.from_url(REDIS_URL)

    # Initialize DB tables if not exist
    init_db()

    # Fetch files
    files = asyncio.run(fetch_pr_files(pr_url))
    print(f"Found {len(files)} files to review")

    for file in files:
        # Run AI review
        result = asyncio.run(review_file(file["filename"], file["patch"]))

        # Save to PostgreSQL
        save_review(pr_url, pr_id, result)
        print(f"Saved review for {file['filename']} to DB")

        # Publish to Redis pub/sub so WebSocket picks it up
        r.publish(f"review:{pr_id}", json.dumps(result))
        print(f"Published review for {file['filename']}")

    # Signal completion
    r.publish(f"review:{pr_id}", json.dumps({"done": True, "pr_id": pr_id}))