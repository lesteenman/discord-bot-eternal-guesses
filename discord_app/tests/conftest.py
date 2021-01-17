import pytest
from eternal_guesses.app import create_app


@pytest.fixture
def client():
    app = create_app()

    # Prepare before your test
    app.config["TESTING"] = True
    app.testing = True

    with app.test_client() as client:
        # Give control to your test
        yield client

    # Cleanup after the test run.

