from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/webhook")
async def github_endpoint(request: Request):
    payload = await request.json()
    print(payload)
    return {"status": "ok"}
