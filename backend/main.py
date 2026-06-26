from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as aioredis
import asyncio
import os
import hashlib
from dotenv import load_dotenv
from kafka_producer import publish_pr_event

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


@app.get("/")
def root():
    return {"status": "AI Code Review Pipeline running"}


@app.post("/review")
async def trigger_review(payload: dict):
    pr_url = payload.get("pr_url")
    if not pr_url:
        return {"error": "pr_url is required"}
    await publish_pr_event(pr_url)
    pr_id = hashlib.md5(pr_url.encode()).hexdigest()[:8]
    return {"status": "Review started", "pr_url": pr_url, "pr_id": pr_id}


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
    finally:
        await redis.close()