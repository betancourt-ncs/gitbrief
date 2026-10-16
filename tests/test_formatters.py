from pathlib import Path
import json
import pytest
from formatters import slack_direct, slack_social

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def read_prompt(filename):
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "formatter, core_file, event_type, pair_file",
    [
        # Checking all possible combinations of formats + events
        pytest.param(slack_social, "SOCIAL_CORE.TXT", "push", "social_push.txt", id="social-push"),
        pytest.param(slack_social, "SOCIAL_CORE.TXT", "pull_request", "social_pr.txt", id="social-pr"),
        pytest.param(slack_social, "SOCIAL_CORE.TXT", "release", "social_release.txt", id="social-release"),
        pytest.param(slack_direct, "DIRECT_CORE.TXT", "push", "direct_push.txt", id="direct-push"),
        pytest.param(slack_direct, "DIRECT_CORE.TXT", "pull_request", "direct_pr.txt", id="direct-pr"),
        pytest.param(slack_direct, "DIRECT_CORE.TXT", "release", "direct_release.txt", id="direct-release"),
    ],
)
def test_build_instructions(formatter, core_file, event_type, pair_file):
    result = formatter.build_instructions(event_type)

    # Building the exact string the function should produce
    expected = read_prompt(core_file) + "\n\n" + read_prompt(pair_file)

    # Check the correct presence and order of relevant files, the absence of unrelated files, and the separator
    assert result == expected


# Mock testing that OpenAI was called with the right arguments and returned the right part of the reply
@pytest.mark.parametrize(
    "formatter, generate_brief, temperature",
    [
        pytest.param(slack_social, slack_social.generate_social_brief, 1.0, id="social"),
        pytest.param(slack_direct, slack_direct.generate_direct_brief, 0.7, id="direct"),
    ],
)
def test_generate_brief_calls_openai(mocker, formatter, generate_brief, temperature):
    # Replace the client dependency with a mock
    mock_client = mocker.patch.object(formatter, "client")

    # Configure what the mock hands back (return_value)
    mock_client.responses.create.return_value.output_text = "fake brief"

    parsed_data = {"event_type": "push", "repo": "test-repo"}

    # Call the real function under test
    result = generate_brief(parsed_data)

    # Assert the output: the function’s return value should be the fake output text
    assert result == "fake brief"

    # Assert the input: ensure the function sent the right arguments to the dependency exactly once
    mock_client.responses.create.assert_called_once_with(
        model="gpt-4o-mini",
        instructions=formatter.build_instructions("push"),
        input=json.dumps(parsed_data),
        temperature=temperature,
        max_output_tokens=300,
    )
