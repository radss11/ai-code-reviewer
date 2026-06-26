import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


async def review_file(filename: str, patch: str) -> dict:
    prompt = f"""You are a senior software engineer doing a code review.
Review this code diff for the file `{filename}`.

Diff:
{patch}

Return a JSON object with this exact structure:
{{
  "filename": "{filename}",
  "summary": "one line summary of what changed",
  "issues": [
    {{
      "severity": "high|medium|low",
      "line": "affected code snippet",
      "comment": "what the issue is and how to fix it"
    }}
  ],
  "verdict": "approved|needs_changes|critical"
}}

Return only valid JSON, no markdown, no extra text."""

    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )
            raw = response.text.strip()
            raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {
                    "filename": filename,
                    "summary": "Could not parse AI response",
                    "issues": [],
                    "verdict": "needs_changes"
                }
        except Exception as e:
            if "503" in str(e) and attempt < 4:
                wait = 5 * (attempt + 1)
                print(f"503 on attempt {attempt + 1}, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise