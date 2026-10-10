from dotenv import load_dotenv
import os
import requests

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

brief = """🚀 *deadmau5* updated _gitbrief_ to include tenant lookup functionality in the webhook handler, modifying server.py. Additionally, the commit addresses missing webhook configuration by making changes to both server.py and slack.py."""
if not SLACK_WEBHOOK_URL:
    raise ValueError("Not found in .env")
response = requests.post(SLACK_WEBHOOK_URL, json={"text": brief}, timeout=10)


print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
