from fastapi import FastAPI, Request, Depends, HTTPException
import json
from payload_parser import parse_push_event
from formatters.slack_social import generate_social_brief
from formatters.slack_direct import generate_direct_brief
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

    # Auth
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

    # Parsing raw payload
    push_data = parse_push_event(payload)

    # Webhook lookup and brief format assignment
    slack_social_url = tenant.social_webhook_url
    slack_direct_url = tenant.direct_webhook_url

    # Social
    social_delivered = False
    if slack_social_url:
        brief = ""
        try:
            brief = generate_social_brief(push_data)
        except Exception as e:
            print(f"Error type: {type(e)}")
            print(f"Detail:'{e}' happened when attempting to generate the social brief for {tenant}")

        if brief:
            try:
                post_to_slack(brief, slack_social_url)
                social_delivered = True
            except Exception as e:
                print(f"Error type: {type(e)}")
                print(
                    f"Detail:'{e}' happened when attempting to post the social brief to {tenant}'s webhook")

    # Direct
    direct_delivered = False
    if slack_direct_url:
        brief = ""

        try:
            brief = generate_direct_brief(push_data)
        except Exception as e:
            print(f"Error type: {type(e)}")
            print(f"Detail:'{e}' happened when attempting to generate the direct brief for {tenant}")

        if brief:
            try:
                post_to_slack(brief, slack_direct_url)
                direct_delivered = True
            except Exception as e:
                print(f"Error type: {type(e)}")
                print(
                    f"Detail:'{e}' happened when attempting to post the direct brief to {tenant}'s webhook")

    # Return status
    if social_delivered == True:
        social_status = "posted"
    elif not slack_social_url:
        social_status = "skipped"
    else:
        social_status = "failed"

    if direct_delivered == True:
        direct_status = "posted"
    elif not slack_direct_url:
        direct_status = "skipped"
    else:
        direct_status = "failed"

    return {
        "social_status": social_status,
        "direct_status": direct_status
    }
