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