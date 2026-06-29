from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as aioredis
import os
import hashlib
from dotenv import load_dotenv
from kafka_producer import publish_pr_event
from database import init_db, get_all_reviews, get_reviews_by_pr

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/")
def root():
    return {"status": "AI Code Review Pipeline running"}


@app.post("/review")
async def trigger_review(payload: dict):
    pr_url = payload.get("pr_url")
    if not pr_url:
        return {"error": "pr_url is required"}
    if "github.com" not in pr_url or "/pull/" not in pr_url:
        return {"error": "Invalid GitHub PR URL. Format: https://github.com/owner/repo/pull/123"}
    try:
        await publish_pr_event(pr_url)
        pr_id = hashlib.md5(pr_url.encode()).hexdigest()[:8]
        return {"status": "Review started", "pr_url": pr_url, "pr_id": pr_id}
    except Exception as e:
        return {"error": f"Failed to publish event: {str(e)}"}


@app.get("/history")
def history():
    try:
        return get_all_reviews()
    except Exception as e:
        return {"error": str(e)}


@app.get("/history/{pr_id}")
def history_by_pr(pr_id: str):
    try:
        return get_reviews_by_pr(pr_id)
    except Exception as e:
        return {"error": str(e)}


@app.websocket("/ws/{pr_id}")
async def websocket_endpoint(websocket: WebSocket, pr_id: str):
    await websocket.accept()
    redis = aioredis.from_url(REDIS_URL)
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"review:{pr_id}")
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"].decode())
    except WebSocketDisconnect:
        await pubsub.unsubscribe(f"review:{pr_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await redis.close()