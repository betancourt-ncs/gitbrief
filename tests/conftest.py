import os
from pathlib import Path
import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient


TESTS_DIR = Path(__file__).parent
PAYLOADS_DIR = TESTS_DIR / "payloads"

TEST_SENDER_ID = 286467853
TEST_SIGNING_SECRET = "test-signing-secret"


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
    from db.base import Base
    import db.models    # pylint: disable=unused-import

    # Setup: fresh in-memory database with tenant table
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = Session(engine)

    yield session   # the test runs here

    # Teardown: runs even if the test fails; the in-memory DB disappears with the engine
    session.close()
    engine.dispose()


# Global fixture (a factory) to insert one tenant into the test db, in any webhook shape
@pytest.fixture
def make_tenant(db_session):
    from db.models import Tenant

    def create_tenant(*, social_webhook_url="https://hooks.slack.test/social", direct_webhook_url="https://hooks.slack.test/direct"):

        tenant = Tenant(
            sender_id=TEST_SENDER_ID,
            signing_secret=TEST_SIGNING_SECRET,
            social_webhook_url=social_webhook_url,
            direct_webhook_url=direct_webhook_url
        )
        db_session.add(tenant)
        db_session.commit()

        return tenant

    return create_tenant


# Global fixture to send requests to the app, with get_db swapped for the test session
# this will connect gitbrief to db_session's created database
@pytest.fixture
def test_client(db_session):
    from server import app
    from db.base import get_db

    # function needed bc dependency_overrides needs to know how to get a session, not be handed a session directly
    def override_get_db():
        yield db_session    # hands over the existing test session (same one db_session and make_tenant use)

    # re-labeling get_db in the endpoint for the test db_session
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)   # the test runs here

    # teardown: remove the swap so it can't leak into other tests
    # this teardown runs before db_session’s, because test_client depends on it
    app.dependency_overrides.clear()


# Notes:

# db_session() fixture:

    # Imports inside fixture:
    #   Not imported at the top of the file bc db.base reads the real DATABASE_URL and builds its engine at import time,
    #   so it must load after pytest_configure sets the fake value
    #   otherwise: an engine pointed at the real gitbrief.db locally (from db.base), and a crash in CI where there's no .env
    #   import db.models: registers the Tenant(Base) model on import, so create_all builds its table (noqa F401)

    # create_engine() args:
    #   sqlite:// : no path after indicates a database stored in RAM. SQLite treats a missing path as its special :memory: database
    #   poolclass=StaticPool: every caller shares ONE connection per engine, so one database
    #       The default pool gives each thread its own connection, and each new in-memory connection (for testing) is a separate, empty DB
    #       My app runs sync endpoints in a worker thread, so without this it can't see the tenants the test seeded
    #   check_same_thread=False: SQLite blocks a connection from being used outside the thread that created it
    #       This arg allows the test thread and the app's worker thread to share this one

    #   Freshness comes from the fixture's scope, not the pool: a new engine per test, and dispose() destroys its DB
    #   StaticPool only controls how connections are shared *within* one engine.


# make_tenant() fixture:

    # create_tenant() args:
    #   * is used as a guard against mixing up the two parameters: it makes every parameter after it keyword-only,
    #   which forces you to name the argument when called, so every call site says exactly which webhook it’s turning off

    #   calling make_tenant() (no args specified) configures both formats, since they are the default parameters


# For integration tests:

    # Pytest builds a fixture once per test and reuses it, so any test using both make_tenant and test_client
    # has one session (created by db_session) shared by all three: the test db, the tenant factory, and the app.
