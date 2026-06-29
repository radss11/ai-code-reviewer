# AI Code Review Pipeline

A production-grade real-time AI code review system. Paste a GitHub PR URL and watch AI-generated review comments stream live to your browser — file by file, as they're generated.

---

## Demo

1. Paste a GitHub PR URL
2. Click **Review**
3. Watch comments stream in live for each file
4. View past reviews via the `/history` endpoint

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
               PostgreSQL (persist results)
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
| **PostgreSQL** | Persistent storage for review history |
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
git clone https://github.com/radss11/ai-code-reviewer.git
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
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/code_review
API_KEY=your_api_key_here
```

**Get your keys:**
- GitHub token: [github.com/settings/tokens](https://github.com/settings/tokens) — select `public_repo` scope
- Gemini API key: [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- API key: any random string you choose

### 3. Create the Kafka topic

```bash
docker compose up -d zookeeper kafka redis postgres
# Wait 30 seconds for Kafka to be healthy, then:
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --create --topic pr-events --partitions 1 --replication-factor 1
```

### 4. Start the full stack

```bash
docker compose up --build -d
```

### 5. Start the Kafka consumer

```bash
docker compose exec kafka-consumer python kafka_consumer.py
```

### 6. Open the dashboard

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

## API

All endpoints except `/` require the `x-api-key` header.

### POST /review
```bash
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_api_key" \
  -d '{"pr_url": "https://github.com/owner/repo/pull/123"}'
```
Response:
```json
{
  "status": "Review started",
  "pr_url": "https://github.com/owner/repo/pull/123",
  "pr_id": "18b7ee84"
}
```

### GET /history
```bash
curl http://localhost:8000/history \
  -H "x-api-key: your_api_key"
```
Returns all past reviews from PostgreSQL.

### GET /history/{pr_id}
```bash
curl http://localhost:8000/history/18b7ee84 \
  -H "x-api-key: your_api_key"
```
Returns reviews for a specific PR.

### WebSocket /ws/{pr_id}
Streams JSON messages as each file is reviewed:
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

## Running Tests

```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows
pip install pytest pytest-asyncio httpx python-dotenv google-genai
pytest tests/ -v
```

Expected output: **9 passed**

---

## Project Structure

```
ai-code-review/
├── backend/
│   ├── main.py              # FastAPI app + WebSocket + auth
│   ├── kafka_producer.py    # Publishes PR events to Kafka
│   ├── kafka_consumer.py    # Consumes events, dispatches Celery tasks
│   ├── celery_app.py        # Celery configuration
│   ├── tasks.py             # Core pipeline: GitHub → AI → DB → Redis
│   ├── github_client.py     # GitHub API — fetch PR diffs
│   ├── ai_client.py         # Gemini AI integration with retry logic
│   ├── database.py          # PostgreSQL — save and retrieve reviews
│   ├── tests/
│   │   ├── test_github_client.py
│   │   └── test_ai_client.py
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
├── .env.example
└── README.md
```

---

## Notes

- Gemini free tier: 20 requests/day on `gemini-2.5-flash-lite`
- Binary files and files without diffs are skipped automatically
- The pipeline retries automatically on 503 errors from Gemini
- Reviews persist in PostgreSQL across restarts