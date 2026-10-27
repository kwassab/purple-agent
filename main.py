from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post("/purple-endpoint")
async def handle_purple_request(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    prompt = data.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="'prompt' field is required")

    return {
        "response": {
            "file_path": "ServerScriptService/Test.lua",
            "content": f'print("Hello, Roblox! Prompt was: {prompt}")'
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "purple-agent"}
