from fastapi import FastAPI, Request
import json

app = FastAPI()


@app.post("/webhook")
async def github_endpoint(request: Request):
    payload = await request.json()
    print(json.dumps(payload, indent=4))
    return {"status": "ok"}
