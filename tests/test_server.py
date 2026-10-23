# INTEGRATION TESTS
import json
import hmac
import hashlib
from payload_parser import parse_push_event
import pytest

# Eligibility status return values per format (built by resolve_status in server.py)
QUEUED = {"status": "queued"}
SKIPPED_NOT_CONFIGURED = {"status": "skipped", "reason": "not_configured"}
SKIPPED_NON_DEFAULT_BRANCH = {"status": "skipped", "reason": "non_default_branch"}

# The sample payload's default_branch is "main"
DEFAULT_BRANCH_REF = "refs/heads/main"
FEATURE_BRANCH_REF = "refs/heads/feature-x"

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


# TESTS BEGIN HERE

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
    tenant = make_tenant()  # both webhooks configured & pushes on the default branch by default
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


# Missing header test: ensure a request with a missing GitHub signature is rejected with a 401
def test_missing_header_returns_401(make_tenant, test_client, load_sample_payload, mocker):
    tenant = make_tenant()
    payload = load_sample_payload("push_default_branch.json")
    mock_social = mocker.patch("server.generate_and_post_social")
    mock_direct = mocker.patch("server.generate_and_post_direct")
    body, headers = build_proper_request(payload, "push", tenant.signing_secret)

    del headers["X-Hub-Signature-256"]    # only variable that changes from happy path
    response = test_client.post("/webhook", content=body, headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}    # no detail in server.py, it returns FastAPI's default detail

    # rejected payloads should never get queued
    mock_social.assert_not_called()
    mock_direct.assert_not_called()


# Bad signature test: ensure a request with a mismatched GitHub signature is rejected with a 401
def test_bad_signature_returns_401(make_tenant, test_client, load_sample_payload, mocker):
    make_tenant()
    payload = load_sample_payload("push_default_branch.json")
    mock_social = mocker.patch("server.generate_and_post_social")
    mock_direct = mocker.patch("server.generate_and_post_direct")
    body, headers = build_proper_request(payload, "push", "wrong-secret")   # only variable that changes from happy path

    response = test_client.post("/webhook", content=body, headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Access denied"}

    mock_social.assert_not_called()
    mock_direct.assert_not_called()


# Skipped formats test: each tenant shape + branch combo reports the right return status per format, and queues only eligible formats
@pytest.mark.parametrize(
    "tenant_webhooks, ref, expected_status_code, expected_social, expected_direct",
    [
        pytest.param({"direct_webhook_url": None}, DEFAULT_BRANCH_REF, 202,
                     QUEUED, SKIPPED_NOT_CONFIGURED, id="social_only"),
        pytest.param({"social_webhook_url": None}, DEFAULT_BRANCH_REF, 202,
                     SKIPPED_NOT_CONFIGURED, QUEUED, id="direct_only"),
        pytest.param({"social_webhook_url": None, "direct_webhook_url": None}, DEFAULT_BRANCH_REF, 200,
                     SKIPPED_NOT_CONFIGURED, SKIPPED_NOT_CONFIGURED, id="zero_destinations"),
        pytest.param({}, FEATURE_BRANCH_REF, 202,
                     SKIPPED_NON_DEFAULT_BRANCH, QUEUED, id="feature_branch_both_configured"),
        pytest.param({"direct_webhook_url": None}, FEATURE_BRANCH_REF, 200,
                     SKIPPED_NON_DEFAULT_BRANCH, SKIPPED_NOT_CONFIGURED, id="feature_branch_social_only"),
        # social skipped both ways (no webhook AND wrong branch): not_configured wins, per the elif order in server.py
        pytest.param({"social_webhook_url": None}, FEATURE_BRANCH_REF, 202,
                     SKIPPED_NOT_CONFIGURED, QUEUED, id="feature_branch_direct_only"),
    ]
)
def test_skipped_formats(tenant_webhooks, ref, expected_status_code, expected_social, expected_direct,
                         make_tenant, test_client, load_sample_payload, mocker):
    tenant = make_tenant(**tenant_webhooks)    # ** unpacks dict into keyword args, makes it clear which webhook is on/off
    payload = load_sample_payload("push_default_branch.json")
    payload["ref"] = ref    # changed before signing, so the signature covers the modified payload
    mock_social = mocker.patch("server.generate_and_post_social")
    mock_direct = mocker.patch("server.generate_and_post_direct")
    body, headers = build_proper_request(payload, "push", tenant.signing_secret)

    response = test_client.post("/webhook", content=body, headers=headers)

    assert response.status_code == expected_status_code
    assert response.json() == {"social_status": expected_social, "direct_status": expected_direct}

    # Ensure queued formats are scheduled for brief generation + posting (skipped formats never are)
    if expected_social == QUEUED:
        mock_social.assert_called_once()
    else:
        mock_social.assert_not_called()

    if expected_direct == QUEUED:
        mock_direct.assert_called_once()
    else:
        mock_direct.assert_not_called()
