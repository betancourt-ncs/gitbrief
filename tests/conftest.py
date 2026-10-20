import os
from pathlib import Path
import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


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


# Global fixture to create an in-memory sqlite db session
@pytest.fixture
def db_session():
    # Imports in here, not at the top: db.base reads the real DATABASE_URL and builds its engine
    # at import time, so it must load after pytest_configure sets the fake value
    # (otherwise: a stale engine locally, and a crash in CI where there's no .env)
    from db.base import Base
    import db.models    # noqa: F401  (registers the Tenant(Base) model on import, so create_all builds its table)

    # Setup: fresh in-memory database with all tables
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)

    yield session   # the test runs here

    # Teardown: runs even if the test fails; the in-memory DB disappears with the engine
    session.close()
    engine.dispose()
