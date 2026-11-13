import pytest
import requests
import slack

SLACK_URL = "https://hooks.slack.com/services/T000/B000/XXXX"


# successful post: the right post request is sent and the response is checked
def test_post_to_slack_sends_message(mocker):
    # mocking dependencies (requests is the dependency, not the 'response' var)
    mock_post = mocker.patch("slack.requests.post")

    slack.post_to_slack("fake brief", SLACK_URL)

    mock_post.assert_called_once_with(SLACK_URL, json={"text": "fake brief"}, timeout=10)

    # to prove the response status is actually checked:
    # .raise_for_status is called but returns nothing on success
    mock_post.return_value.raise_for_status.assert_called_once()


# Slack rejects the post (4xx/5xx): the error must transmit to the caller
def test_post_to_slack_raises_on_http_error(mocker):
    mock_post = mocker.patch("slack.requests.post")

    # setup the response that the mocked requests.post will hand back when called
    fake_slack_response = mock_post.return_value    # blank stand-in response object
    fake_slack_response.raise_for_status.side_effect = requests.HTTPError(response=fake_slack_response)  # raise HTTPError on raise_for_status call

    # using pytest.raises since raising is the correct behavior here, not an error
    with pytest.raises(requests.HTTPError):    # passes test only if the block raises this exception
        slack.post_to_slack("fake brief", SLACK_URL)

    # same as:
        #     try:
        #         slack.post_to_slack("fake brief", SLACK_URL)
        #     except requests.HTTPError:
        #         pass                           # raised the expected error: success
        #     else:
        #         pytest.fail("DID NOT RAISE")   # no error at all: failure
