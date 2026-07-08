import requests
import os
from dotenv import load_dotenv

load_dotenv()


def post_to_slack(message: str):
    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    if not slack_url:
        raise ValueError("SLACK_WEBHOOK_URL not found in environment")

    payload = {"text": message}

    requests.post(slack_url, json=payload, timeout=10)


# Test
if __name__ == "__main__":
    post_to_slack("Time to party")
