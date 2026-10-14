from types import SimpleNamespace
import pytest
from filters import is_social_eligible, is_direct_eligible

WEBHOOK_URL = "https://hooks.slack.com/services/T000/B000/XXXX"


@pytest.mark.parametrize(
    "social_webhook_url, parsed_data, expected",
    [
        pytest.param(
            None,
            {"event_type": "push", "branch": "main", "default_branch": "main"},
            False,
            id="no-webhook",
        ),
        pytest.param(
            "",
            {"event_type": "push", "branch": "main", "default_branch": "main"},
            False,
            id="empty-string-webhook",
        ),
        pytest.param(
            WEBHOOK_URL,
            {"event_type": "push", "branch": "main", "default_branch": "main"},
            True,
            id="push-default-branch",
        ),
        pytest.param(
            WEBHOOK_URL,
            {"event_type": "push", "branch": "feature-x", "default_branch": "main"},
            False,
            id="push-feature-branch",
        ),
        pytest.param(
            WEBHOOK_URL,
            {"event_type": "push", "branch": None, "default_branch": "main"},
            False,
            id="tag-push",
        ),
        pytest.param(
            WEBHOOK_URL,
            {"event_type": "push", "branch": "master", "default_branch": "master"},
            True,
            id="push-non-main-default-branch",
        ),
        pytest.param(
            WEBHOOK_URL,
            {"event_type": "pull_request"},
            True,
            id="pr-merged"
        ),
        pytest.param(
            WEBHOOK_URL,
            {"event_type": "release"},
            True,
            id="release",
        ),
    ]
)
def test_is_social_eligible(social_webhook_url, parsed_data, expected):
    tenant = SimpleNamespace(social_webhook_url=social_webhook_url)
    result = is_social_eligible(tenant, parsed_data)
    assert result is expected


@pytest.mark.parametrize(
    "direct_webhook_url, expected",
    [
        pytest.param(WEBHOOK_URL, True, id="configured"),
        pytest.param(None, False, id="not-configured"),
        pytest.param("", False, id="empty-string"),
    ]
)
def test_is_direct_eligible(direct_webhook_url, expected):
    tenant = SimpleNamespace(direct_webhook_url=direct_webhook_url)
    result = is_direct_eligible(tenant)
    assert result is expected
