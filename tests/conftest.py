import pytest
from app import create_app
from app import extensions
from app.models.base import Base

@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for the test session"""
    app = create_app("testing")
    yield app

@pytest.fixture(scope="function")
def db(app):
    """Create a clean database for every test"""
    with app.app_context():
        # Access engine dynamically via the module
        Base.metadata.create_all(bind=extensions.engine)
        yield extensions.db_session
        extensions.db_session.remove()
        Base.metadata.drop_all(bind=extensions.engine)

@pytest.fixture(scope="function")
def client(app, db):
    """A test client for the app"""
    return app.test_client()