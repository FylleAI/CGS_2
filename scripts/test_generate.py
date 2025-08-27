import requests
import sys

BASE_URL = "http://localhost:8000"

payload = {
    "topic": "AI nel Fintech",
    "workflow_type": "enhanced_article",
    "client_profile": "default",
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 0.7,
    "target_word_count": 800,
    "target_audience": "investitori retail",
    "tone": "professionale",
    "include_statistics": True,
    "include_examples": True,
    "context": "focus su trend 2025 e impatto normativo"
}

if __name__ == "__main__":
    try:
        print("Calling /api/v1/content/generate ...")
        r = requests.post(f"{BASE_URL}/api/v1/content/generate", json=payload, timeout=600)
        print("Status:", r.status_code)
        data = r.json()
        print("Title:", data.get("title"))
        body = data.get("body", "")
        print("Body preview:", body[:300].replace("\n", " ") + ("..." if len(body) > 300 else ""))
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

