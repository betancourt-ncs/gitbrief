# INTEGRATION TESTS
import json
import hmac
import hashlib


# helper function to build a properly signed request for every test
# mimics what GitHub would send: body bytes & signed headers (the test does the posting using test_client fixture)
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


# Unknown sender test: tenant not found in db, so the lookup rejects before auth (no signature needed)
def test_unknown_sender_returns_404(test_client, load_sample_payload):
    # empty test DB since make_tenant is never called
    payload = load_sample_payload("push_default_branch.json")

    # TestClient sends a post request to my app endpoint (mimicking GitHub) & returns the response
    response = test_client.post("/webhook", json=payload)

    # assert gitbrief returned correct status code (404) and body (response.json())
    assert response.status_code == 404
    assert response.json() == {"detail": "Error: User not found"}   # confirms that MY tenant lookup line produced this 404
