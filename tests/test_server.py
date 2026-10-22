# INTEGRATION TESTS
import json
import hmac
import hashlib


# helper function to build a properly signed request for every test
# mimics what GitHub would send: body bytes plus signed headers (the test does the posting using test_client fixture)
def build_proper_request(payload, event_type, secret):
    body = json.dumps(payload).encode()     # serialize the sample payload to bytes (to be signed and sent)

    # signing those exact bytes with the test tenant’s secret (same as GitHub's HMAC-SHA256 computation)
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": event_type,
        "X-GitHub-Delivery": "test-delivery-id",   # any string; the endpoint only logs it
    }

    return body, headers
