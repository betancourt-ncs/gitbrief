# INTEGRATION TESTS
import json
import hmac
import hashlib
from payload_parser import parse_push_event


# helper function to build a properly signed request for every test
# mimics what GitHub would send: body bytes & signed headers (the test does the posting using test_client fixture)
def build_proper_request(payload, event_type, signing_secret):
    body = json.dumps(payload).encode()     # serialize the sample payload to bytes (to be signed and sent)

    # signing those exact bytes with the test tenant’s secret (same as GitHub's HMAC-SHA256 computation)
    signature = "sha256=" + hmac.new(signing_secret.encode(), body, hashlib.sha256).hexdigest()

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


# Happy path test: a signed and verified payload returns 202, eligible formats are queued for generation + posting
def test_valid_sender_returns_202(make_tenant, test_client, load_sample_payload, mocker):
    tenant = make_tenant()
    payload = load_sample_payload("push_default_branch.json")
    mock_social = mocker.patch("server.generate_and_post_social")
    mock_direct = mocker.patch("server.generate_and_post_direct")
    body, headers = build_proper_request(payload, "push", tenant.signing_secret)

    parsed_payload = parse_push_event(payload)
    parsed_payload["event_type"] = "push"

    response = test_client.post("/webhook", content=body, headers=headers)

    assert response.status_code == 202
    assert response.json() == {"social_status": {"status": "queued"}, "direct_status": {"status": "queued"}}

    mock_social.assert_called_once_with(parsed_payload, tenant.social_webhook_url, "test-delivery-id", tenant.id)
    mock_direct.assert_called_once_with(parsed_payload, tenant.direct_webhook_url, "test-delivery-id", tenant.id)
