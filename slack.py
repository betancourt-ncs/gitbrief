import requests


def post_to_slack(message: str, slack_url: str):

    payload = {"text": message}

    requests.post(slack_url, json=payload, timeout=10)
