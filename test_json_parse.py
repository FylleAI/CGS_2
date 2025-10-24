import json

body = """```json
{
  "company_score": 91,
  "content_opportunities": [
    {
      "type": "blog_post",
      "topic": "Test",
      "priority": "high",
      "estimated_reach": 75000,
      "engagement_potential": 9.0,
      "rationale": "Test"
    }
  ],
  "optimization_insights": {
    "brand_voice": {
      "score": 92,
      "status": "strong",
      "recommendation": "Test",
      "quick_wins": ["Test"]
    }
  },
  "competitors": [],
  "quick_wins": [],
  "full_report": "Test"
}
```"""

# Remove markdown code blocks if present
if body.strip().startswith("```"):
    # Extract JSON from markdown code block
    lines = body.strip().split("\n")
    # Remove first line (```json or ```)
    if lines[0].startswith("```"):
        lines = lines[1:]
    # Remove last line (```)
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    body = "\n".join(lines)

print("Cleaned body:")
print(body)
print("\n" + "="*80 + "\n")

# Parse JSON
try:
    analytics_data = json.loads(body.strip())
    print("✅ JSON parsed successfully!")
    print(f"Keys: {list(analytics_data.keys())}")
except json.JSONDecodeError as e:
    print(f"❌ JSON parsing failed: {e}")

