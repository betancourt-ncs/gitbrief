import os
from pathlib import Path
import json
import pytest

TESTS_DIR = Path(__file__).parent
PAYLOADS_DIR = TESTS_DIR / "payloads"


# Hook to apply these variables automatically to every test (runs once before test collection)
def pytest_configure():
    os.environ["OPENAI_API_KEY"] = "test-key-not-real"
    os.environ["SLACK_WEBHOOK_URL"] = "fake-slack-url"
    os.environ["DATABASE_URL"] = "sqlite://"


# Global fixture to load a specific sample Github payload in tests
@pytest.fixture
def load_sample_payload():
    def load_filename(filename):
        with open(PAYLOADS_DIR / filename) as f:
            return json.load(f)
    return load_filename
