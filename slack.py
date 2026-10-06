import requests


def post_to_slack(message: str, slack_url: str):

    payload = {"text": message}

    response = requests.post(slack_url, json=payload, timeout=10)

    # Raises requests.HTTPError on any 4xx/5xx (e.g. 404 on a revoked webhook)
    response.raise_for_status()
