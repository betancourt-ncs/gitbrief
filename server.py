from fastapi import FastAPI, Request, Depends, HTTPException
import json
from payload_parser import parse_push_event
from formatters.slack_social import generate_social_brief
from slack import post_to_slack
from db.base import Base, engine, get_db
import db.models  # pylint: disable=unused-import
from db.crud import get_tenant
from sqlalchemy.orm import Session
from auth import verify_signature

app = FastAPI()

# Creating the db tables
Base.metadata.create_all(engine)


@app.post("/webhook")
async def github_endpoint(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()
    payload = json.loads(raw_body)

    sender_id = payload["sender"]["id"]

    tenant = get_tenant(db, sender_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Error: User not found")

    github_signature = request.headers.get("X-Hub-Signature-256")
    if not github_signature:
        raise HTTPException(status_code=401)

    secret_key = tenant.signing_secret

    verified_signature = verify_signature(
        raw_body, secret_key, github_signature)
    if not verified_signature:
        raise HTTPException(status_code=401, detail="Access denied")

    push_data = parse_push_event(payload)

    brief = generate_social_brief(push_data)

    post_to_slack(brief)

    return {"status": "ok"}
