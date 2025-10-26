import os
import importlib
import pytest
from sqlalchemy import text

@pytest.fixture(scope="session")
def test_database_url():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to a PostGIS database to run these tests.")
    return url

@pytest.fixture(scope="session")
def app(test_database_url, monkeypatch):
    """
    Import the app after pointing DATABASE_URL at the test DB.
    """
    # Ensure the app imports with the test DB
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    # Import the target module fresh with the env applied
    home = importlib.import_module("home")

    # Sanity: create tables via the provided endpoint
    with home.app.test_client() as c:
        r = c.post("/db/init")
        assert r.status_code == 200

    # Clean DB before running the session
    with home.app.app_context():
        from home import db
        db.session.execute(text("DELETE FROM locations"))
        db.session.commit()

    yield home.app

        # Optionally, clean after the whole session
    with home.app.app_context():
        from home import db
        db.session.execute(text("DELETE FROM locations"))
        db.session.commit()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def db_session(app):
    from home import db
    with app.app_context():
        yield db.session
        db.session.rollback()