import os


# Hook to apply these variables automatically to every single test (runs once before test collection)
def pytest_configure():
    os.environ["OPENAI_API_KEY"] = "test-key-not-real"
    os.environ["SLACK_WEBHOOK_URL"] = "fake-slack-url"
    os.environ["DATABASE_URL"] = "sqlite://"
