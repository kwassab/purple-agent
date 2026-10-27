import os
from fastapi import FastAPI, Request, HTTPException
import requests
from typing import Any, Dict

app = FastAPI()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY environment variable is not set")

@app.post("/purple-endpoint")
async def handle_purple_request(request: Request) -> Dict[str, Any]:
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    user_prompt = data.get("prompt", "")
    if not user_prompt:
        raise HTTPException(status_code=400, detail="'prompt' field is required")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://www.purple.ai",
        "X-Title": "Purple Integration"
    }

    payload = {
        "model": "anthropic/claude-3-5-sonnet-20240620",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты — эксперт по Roblox Lua. Твоя задача — не просто писать код, "
                    "а подготовить ответ для инструмента авто-применения. Ты должен вернуть "
                    "ТОЛЬКО JSON объект с ключами: file_path (путь к файлу в проекте), "
                    "content (полный новый код файла). Не пиши никаких пояснений, только JSON."
                )
            },
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        response_data = resp.json()
        ai_response = response_data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="OpenRouter request timed out")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error calling OpenRouter: {str(e)}")
    except (KeyError, IndexError):
        raise HTTPException(status_code=502, detail="Invalid response format from OpenRouter")

    return {"response": ai_response}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "purple-agent"}
