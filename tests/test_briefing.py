import logging

import pytest
import requests

import briefing

SLACK_URL = "https://hooks.slack.com/services/T000/B000/XXXX"
PARSED_DATA = {"event_type": "push", "repo": "test-repo"}


# Testing all of generate_and_post_x's expected outcomes/scenarios play out as they should by recording what was logged

INPUTS = [
    pytest.param(briefing.generate_and_post_social, "briefing.generate_social_brief", "Social", id="social"),
    pytest.param(briefing.generate_and_post_direct, "briefing.generate_direct_brief", "Direct", id="direct"),
]


# happy path
@pytest.mark.parametrize("generate_and_post_x, generate_x_brief, label", INPUTS)
def test_happy_path_posts_brief(mocker, caplog, generate_and_post_x, generate_x_brief, label):
    caplog.set_level(logging.INFO)

    # Mocking dependencies
    mock_generation = mocker.patch(generate_x_brief)
    mock_generation.return_value = "fake brief"
    mock_post = mocker.patch("briefing.post_to_slack")

    generate_and_post_x(PARSED_DATA, SLACK_URL, "delivery-123", 1)

    mock_post.assert_called_once_with("fake brief", SLACK_URL)  # asserting correct mock inputs were used
    assert f"{label} brief delivered to Slack" in caplog.text   # ensures function successfully generated and posted to Slack
    assert "delivery_id=delivery-123" in caplog.text    # proves function takes the delivery_id passed to it and puts it into its log output


# generation fails (OpenAI error, timeout, etc.)
@pytest.mark.parametrize("generate_and_post_x, generate_x_brief, label", INPUTS)
def test_generation_failure_skips_slack(mocker, caplog, generate_and_post_x, generate_x_brief, label):
    # Mocking dependencies
    mock_generation = mocker.patch(generate_x_brief)
    mock_generation.side_effect = RuntimeError("OpenAI down")   # .side_effect makes the mock raise instead of returning
    mock_post = mocker.patch("briefing.post_to_slack")

    generate_and_post_x(PARSED_DATA, SLACK_URL, "delivery-123", 1)   # must not raise: the error is caught inside the function

    mock_generation.assert_called_once()   # proves the failure came from this mock, not a real OpenAI call
    mock_post.assert_not_called()   # nothing to send, so Slack is never contacted

    assert f"{label} brief generation failed" in caplog.text    # ensure it's logged with the right wording
    assert caplog.records[-1].levelname == "ERROR"   # ensure it's logged at the right severity


# generation succeeds, but returns empty text
@pytest.mark.parametrize("generate_and_post_x, generate_x_brief, label", INPUTS)
def test_empty_brief_skips_slack(mocker, caplog, generate_and_post_x, generate_x_brief, label):
    # Mocking dependencies
    mock_generation = mocker.patch(generate_x_brief)
    mock_generation.return_value = ""
    mock_post = mocker.patch("briefing.post_to_slack")

    generate_and_post_x(PARSED_DATA, SLACK_URL, "delivery-123", 1)

    mock_post.assert_not_called()   # an empty brief is never posted
    assert f"{label} brief generation returned empty output" in caplog.text


# Slack rejects the post (4xx/5xx, e.g. 404 on a revoked webhook)
@pytest.mark.parametrize("generate_and_post_x, generate_x_brief, label", INPUTS)
def test_slack_http_error_logs_status(mocker, caplog, generate_and_post_x, generate_x_brief, label):
    # Mocking dependencies
    mock_generation = mocker.patch(generate_x_brief)
    mock_generation.return_value = "fake brief"

    mock_post = mocker.patch("briefing.post_to_slack")
    fake_slack_response = mocker.Mock(status_code=404)  # stand-in for what response.raise_for_status() would attach to the error (check slack.py)
    mock_post.side_effect = requests.HTTPError(response=fake_slack_response)

    generate_and_post_x(PARSED_DATA, SLACK_URL, "delivery-123", 1)

    assert f"{label} brief delivery failed: Slack returned 404" in caplog.text  # ensures the status code reaches the log (also guards the except-block order)


# Slack unreachable (timeout, connection error)
@pytest.mark.parametrize("generate_and_post_x, generate_x_brief, label", INPUTS)
def test_slack_timeout_logs_error_type(mocker, caplog, generate_and_post_x, generate_x_brief, label):
    # Mocking dependencies
    mock_generation = mocker.patch(generate_x_brief)
    mock_generation.return_value = "fake brief"

    mock_post = mocker.patch("briefing.post_to_slack")
    mock_post.side_effect = requests.Timeout()

    generate_and_post_x(PARSED_DATA, SLACK_URL, "delivery-123", 1)

    assert f"{label} brief delivery failed: Timeout" in caplog.text   # ensures the error type's name reaches the log
