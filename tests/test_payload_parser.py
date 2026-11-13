import pytest
from payload_parser import parse_push_event, parse_pr_event, parse_release_event


# Push
def test_parse_push_event(load_sample_payload):
    payload = load_sample_payload("push_default_branch.json")
    parsed_payload = parse_push_event(payload)
    assert parsed_payload["ref_type"] == "heads"
    assert parsed_payload["branch"] == "main"
    assert parsed_payload["default_branch"] == "main"
    assert parsed_payload["repo"] == "test-repo"
    assert parsed_payload["pusher"] == "betancourt-ncs"
    assert parsed_payload["commits"][0]["message"] == "Add Flask API with route definitions and request validation schemas"
    assert len(parsed_payload["commits"]) == 2
    assert "tag" not in parsed_payload


# Tag push
def test_parse_push_event_tag(load_sample_payload):
    payload = load_sample_payload("push_default_branch.json")
    payload["ref"] = "refs/tags/v1.0.0"
    parsed_payload = parse_push_event(payload)
    assert parsed_payload["ref_type"] == "tags"
    assert parsed_payload["branch"] is None
    assert parsed_payload["tag"] == "v1.0.0"


# Pull request
def test_parse_pr_event(load_sample_payload):
    payload = load_sample_payload("pr_merged.json")
    parsed_payload = parse_pr_event(payload)
    assert parsed_payload["title"] == "Testing PR event"
    assert parsed_payload["body"] == "I created a test-branch to add the tenant's singing secret creation and the Base model class of the tenant in the db."
    assert parsed_payload["username"] == "betancourt-ncs"
    assert parsed_payload["repo"] == "betancourt-ncs/test-repo"
    assert parsed_payload["head_branch"] == "test-branch"
    assert parsed_payload["base_branch"] == "main"
    assert parsed_payload["pr_number"] == 1
    assert parsed_payload["commits"] == 3
    assert parsed_payload["additions"] == 39
    assert parsed_payload["deletions"] == 0
    assert parsed_payload["changed_files"] == 3


# Pull request with a missing/empty body
@pytest.mark.parametrize(
    "empty_body",
    [
        pytest.param(None, id="null-body"),
        pytest.param("", id="empty-string-body"),
    ],
)
def test_parse_pr_event_missing_body(load_sample_payload, empty_body):
    payload = load_sample_payload("pr_merged.json")
    payload["pull_request"]["body"] = empty_body
    parsed_payload = parse_pr_event(payload)
    assert parsed_payload["body"] == "No description provided"


# Release
def test_parse_release_event(load_sample_payload):
    payload = load_sample_payload("release_published.json")
    parsed_payload = parse_release_event(payload)
    assert parsed_payload["action"] == "published"
    assert parsed_payload["tag_name"] == "v2.0.0-beta.1"
    assert parsed_payload["release_name"] == "v2.0.0-beta.1 — Early Preview"
    assert parsed_payload["prerelease"] is True
    assert parsed_payload["author_login"] == "betancourt-ncs"
    assert parsed_payload["repo"] == "test-repo"
    assert parsed_payload["target_commitish"] == "main"
    assert parsed_payload["html_url"] == "https://github.com/betancourt-ncs/test-repo/releases/tag/v2.0.0-beta.1"
    assert parsed_payload["body"].startswith("## v2.0.0-beta.1 — Early Preview")
