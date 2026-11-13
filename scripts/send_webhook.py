import json
import os
import hmac
import hashlib
import requests
from dotenv import load_dotenv
from payload_parser import parse_push_event


fake_payload = {
    "ref": "refs/heads/main",
    "sender": {
        "id": 286467853},
    "commits": [
        {"message": "Add Flask API with route definitions and request validation schemas",
         "added":   ["app.py",
                     "requirements.txt",
                     "routes.py",
                     "schema.py"],
         "removed": [],
         "modified": []
         }],
    "repository": {
        "name": "my-repo",
        "default_branch": "main"},
    "pusher": {
        "name": "betancourt-ncs"}
}


raw_body = json.dumps(fake_payload).encode("utf-8")

parsed_data = parse_push_event(fake_payload)
parsed_data['event_type'] = "push"

if __name__ == "__main__":
    load_dotenv()
    SIGNING_SECRET = os.getenv("LOCAL_SIGNING_SECRET")
    if not SIGNING_SECRET:
        raise ValueError("Not found in .env")

    SIGNING_SECRET_BYTES = SIGNING_SECRET.encode("utf-8")
    test_hmac = "sha256=" + \
        hmac.new(SIGNING_SECRET_BYTES, raw_body, hashlib.sha256).hexdigest()

    response = requests.post("http://127.0.0.1:8000/webhook", data=raw_body,
                             headers={
                                 "X-Hub-Signature-256": test_hmac,
                                 "X-GitHub-Delivery": "1ce88066-a64d-11f1-90fe-bc5f87e66eca",
                                 "X-GitHub-Event": "push",
                                 "Content-Type": "application/json"},
                             timeout=10)

    print(response.text)
