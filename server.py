from fastapi import FastAPI, Request
from payload_parser import parse_push_event
from formatters.slack_social import generate_social_brief
from slack import post_to_slack

app = FastAPI()


@app.post("/webhook")
async def github_endpoint(request: Request):
    payload = await request.json()

    push_data = parse_push_event(payload)

    brief = generate_social_brief(push_data)

    post_to_slack(brief)

    return {"status": "ok"}
