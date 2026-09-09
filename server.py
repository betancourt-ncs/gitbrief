from fastapi import FastAPI, Request, Depends, HTTPException
import json
from payload_parser import parse_push_event, parse_pr_event, parse_release_event
from formatters.slack_social import generate_social_brief
from formatters.slack_direct import generate_direct_brief
from slack import post_to_slack
from db.base import Base, engine, get_db
import db.models  # pylint: disable=unused-import
from db.crud import get_tenant
from sqlalchemy.orm import Session
from auth import verify_signature
from filters import is_social_eligible, is_direct_eligible
from datetime import datetime

app = FastAPI()

# Creating the db tables
Base.metadata.create_all(engine)


# Dependency for getting Github payload as bytes
async def get_payload_bytes(request: Request):
    return await request.body()


@app.post("/webhook")
def github_endpoint(request: Request, body: bytes = Depends(get_payload_bytes), db: Session = Depends(get_db)):

    # Loading payload body as bytes
    payload = json.loads(body)

    # Debugging
    print(f"{datetime.now()} - event: {request.headers.get('X-GitHub-Event')} - action: {payload.get('action') if request.headers.get('X-GitHub-Event') == 'release' else 'n/a'}")

    # Auth
    sender_id = payload["sender"]["id"]

    tenant = get_tenant(db, sender_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Error: User not found")

    github_signature = request.headers.get("X-Hub-Signature-256")
    if not github_signature:
        raise HTTPException(status_code=401)

    secret_key = tenant.signing_secret

    verified_signature = verify_signature(body, secret_key, github_signature)
    if not verified_signature:
        raise HTTPException(status_code=401, detail="Access denied")

    # Event type retrieval and parsing raw payload
    event_type = request.headers.get("X-GitHub-Event")

    if event_type == "push":
        parsed_data = parse_push_event(payload)
        parsed_data['event_type'] = event_type

    elif event_type == "pull_request":
        action = payload.get("action")
        merged = payload.get("pull_request", {}).get("merged", False)
        if not (action == "closed" and merged):
            return {"status": "ignored", "reason": "PR not closed and merged"}
        parsed_data = parse_pr_event(payload)
        parsed_data['event_type'] = event_type

    elif event_type == "release":
        action = payload.get("action")
        # Guarding against "draft" releases and double briefs when published
        if not (action == "released" or (action == "published" and payload.get("release").get("prerelease"))):
            return {"status": "ignored", "reason": "release not live and stable"}
        parsed_data = parse_release_event(payload)
        parsed_data['event_type'] = event_type

    else:
        return {"status": "ignored", "reason": "event type not handled by gitbrief"}

    # Webhook lookup and brief format assignment
    slack_social_url = tenant.social_webhook_url
    slack_direct_url = tenant.direct_webhook_url

    # Social
    social_delivered = False
    social_eligible = is_social_eligible(tenant, parsed_data)

    if social_eligible:
        brief = ""
        try:
            brief = generate_social_brief(parsed_data)
        except Exception as e:
            print(f"Error type: {type(e)}")
            print(f"Detail:'{e}' happened when attempting to generate the social brief for {tenant}")

        if brief:
            try:
                assert slack_social_url is not None
                post_to_slack(brief, slack_social_url)
                social_delivered = True
            except Exception as e:
                print(f"Error type: {type(e)}")
                print(
                    f"Detail:'{e}' happened when attempting to post the social brief to {tenant}'s webhook")

    # Direct
    direct_delivered = False
    direct_eligible = is_direct_eligible(tenant)

    if direct_eligible:
        brief = ""

        try:
            brief = generate_direct_brief(parsed_data)
        except Exception as e:
            print(f"Error type: {type(e)}")
            print(f"Detail:'{e}' happened when attempting to generate the direct brief for {tenant}")

        if brief:
            try:
                assert slack_direct_url is not None
                post_to_slack(brief, slack_direct_url)
                direct_delivered = True
            except Exception as e:
                print(f"Error type: {type(e)}")
                print(
                    f"Detail:'{e}' happened when attempting to post the direct brief to {tenant}'s webhook")

    # Return status
    if social_delivered == True:
        social_status = {"status": "posted"}
    elif not social_eligible:
        social_status = {"status": "skipped"}
    else:
        social_status = {"status": "failed"}

    if direct_delivered == True:
        direct_status = {"status": "posted"}
    elif not direct_eligible:
        direct_status = {"status": "skipped"}
    else:
        direct_status = {"status": "failed"}

    return {
        "social_status": social_status,
        "direct_status": direct_status
    }
