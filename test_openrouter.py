import requests
import json

# Test OpenRouter directly
resp = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    },
    json={
        "model": "openrouter/free",
        "messages": [{"role": "user", "content": "Say OK"}]
    },
    timeout=30
)
print(f"OpenRouter Status: {resp.status_code}")
print(f"OpenRouter Response: {resp.text[:200]}")
