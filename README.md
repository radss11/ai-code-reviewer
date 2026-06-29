# AI Code Review Pipeline

A production-grade real-time AI code review system. Paste a GitHub PR URL and watch AI-generated review comments stream live to your browser — file by file, as they're generated.

---

## Demo

1. Paste a GitHub PR URL
2. Click **Review**
3. Watch comments stream in live for each file

---

## Architecture

```
GitHub PR URL
     │
     ▼
 FastAPI (POST /review)
     │
     ▼
 Kafka (pr-events topic)
     │
     ▼
 Kafka Consumer → Celery Task
                      │
                      ▼
               GitHub API (fetch diff)
                      │
                      ▼
               Gemini AI (review each file)
                      │
                      ▼
               Redis pub/sub
                      │
                      ▼
         FastAPI WebSocket → Browser
```

---

## Tech Stack

| Technology | Role |
|---|---|
| **FastAPI** | Backend gateway + WebSocket server |
| **Kafka** | Message broker — decouples ingestion from processing |
| **Celery** | Async task workers — parallel file analysis |
| **Redis** | Celery broker + WebSocket pub/sub channel |
| **Gemini AI** | AI review engine |
| **React + Vite** | Frontend dashboard |
| **Docker Compose** | Runs the entire stack with one command |

---

## Prerequisites

- Docker Desktop
- Git Bash (Windows) or Terminal (Mac/Linux)
- GitHub personal access token
- Google Gemini API key (free tier)

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/ai-code-reviewer.git
cd ai-code-reviewer
```

### 2. Create `.env` file

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```
GITHUB_TOKEN=your_github_token_here
GEMINI_API_KEY=your_gemini_key_here
REDIS_URL=redis://redis:6379/0
KAFKA_BROKER=kafka:9092
```

**Get your keys:**
- GitHub token: [github.com/settings/tokens](https://github.com/settings/tokens) — select `public_repo` scope
- Gemini API key: [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 3. Create the Kafka topic

```bash
docker compose up -d zookeeper kafka redis
# Wait 30 seconds for Kafka to be healthy, then:
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --create --topic pr-events --partitions 1 --replication-factor 1
```

### 4. Start the full stack

```bash
docker compose up --build -d
```

### 5. Open the dashboard

```
http://localhost:3000
```

Paste any public GitHub PR URL and click **Review**.

---

## Services

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Project Structure

```
ai-code-review/
├── backend/
│   ├── main.py              # FastAPI app + WebSocket
│   ├── kafka_producer.py    # Publishes PR events to Kafka
│   ├── kafka_consumer.py    # Consumes events, dispatches Celery tasks
│   ├── celery_app.py        # Celery configuration
│   ├── tasks.py             # Core pipeline: GitHub → AI → Redis
│   ├── github_client.py     # GitHub API — fetch PR diffs
│   ├── ai_client.py         # Gemini AI integration
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── PRInput.jsx
│       │   └── ReviewFeed.jsx
│       └── hooks/
│           └── useWebSocket.js
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docker-compose.yml
└── .env.example
```

---

## How It Works

1. **POST /review** — FastAPI receives the PR URL and publishes it to Kafka
2. **Kafka consumer** — picks up the event and dispatches a Celery task
3. **Celery worker** — fetches the PR diff from GitHub API
4. **Gemini AI** — reviews each changed file in parallel, returns structured JSON
5. **Redis pub/sub** — worker publishes each file's review to a channel
6. **WebSocket** — FastAPI subscribes to Redis and streams results to the browser
7. **React frontend** — renders review cards live as each file finishes

---

## API

### POST /review
```json
{
  "pr_url": "https://github.com/owner/repo/pull/123"
}
```
Response:
```json
{
  "status": "Review started",
  "pr_url": "https://github.com/owner/repo/pull/123",
  "pr_id": "18b7ee84"
}
```

### WebSocket /ws/{pr_id}
Streams JSON messages:
```json
{
  "filename": "src/main.py",
  "summary": "Adds input validation to the review endpoint",
  "issues": [
    {
      "severity": "high",
      "line": "if not pr_url:",
      "comment": "Missing error message in response"
    }
  ],
  "verdict": "needs_changes"
}
```

---

## Notes

- Gemini free tier: 20 requests/day on `gemini-2.5-flash-lite`
- Binary files and files without diffs are skipped automatically
- The pipeline retries automatically on 503 errors from Gemini