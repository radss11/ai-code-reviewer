import psycopg2  # type: ignore
import psycopg2.extras # type: ignore
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            pr_url TEXT NOT NULL,
            pr_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            summary TEXT,
            verdict TEXT,
            issues JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized")


def save_review(pr_url: str, pr_id: str, review: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reviews (pr_url, pr_id, filename, summary, verdict, issues)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        pr_url,
        pr_id,
        review.get("filename"),
        review.get("summary"),
        review.get("verdict"),
        psycopg2.extras.Json(review.get("issues", []))
    ))
    conn.commit()
    cur.close()
    conn.close()


def get_all_reviews():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT pr_url, pr_id, filename, summary, verdict, issues, created_at
        FROM reviews
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "pr_url": r[0],
            "pr_id": r[1],
            "filename": r[2],
            "summary": r[3],
            "verdict": r[4],
            "issues": r[5],
            "created_at": r[6].isoformat()
        }
        for r in rows
    ]


def get_reviews_by_pr(pr_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT pr_url, pr_id, filename, summary, verdict, issues, created_at
        FROM reviews
        WHERE pr_id = %s
        ORDER BY created_at DESC
    """, (pr_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "pr_url": r[0],
            "pr_id": r[1],
            "filename": r[2],
            "summary": r[3],
            "verdict": r[4],
            "issues": r[5],
            "created_at": r[6].isoformat()
        }
        for r in rows
    ]