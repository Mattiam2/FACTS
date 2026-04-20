import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import StaticPool, SQLModel, Session
from sqlmodel import create_engine

from src.core.config import Settings
from src.main import app


@pytest.fixture(name="test_engine")
def test_engine_fixture():
    """
    Creates an in-memory SQLite engine.
    StaticPool ensures that all connections
    go to the same in-memory database.
    """
    sqlite_url = "sqlite://"
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        execution_options={"schema_translate_map": {"public": None}}
    )
    yield engine

    # Clean up after tests are done
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(name="session")
def session_fixture(test_engine):
    """
    Create a pytest fixture for a database session using the given test engine.
    """
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(test_engine):
    """
    Patches the engine in the middleware module with the test_engine,
    then provides the TestClient.
    """

    os.environ["JWT_VERIFY_EXP"] = "0"

    patch_middleware = patch("src.main.engine", test_engine)

    patch_lifespan = patch("src.repositories.engine", test_engine)

    test_settings = Settings(JWT_VERIFY_EXP=False)

    patch_settings_auth = patch("src.core.auth.settings", test_settings)
    patch_settings_auth_services = patch("src.services.authorisation.settings", test_settings)

    with patch_middleware, patch_lifespan, patch_settings_auth, patch_settings_auth_services:
        with TestClient(app) as client:
            yield client