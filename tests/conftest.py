import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure test settings
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-12345"

from app.core.database import Base
from app.dependencies.database import get_db
from app.main import app
from app.models.client import Client
from app.utils.security import hash_secret, create_access_token

# Setup test in-memory SQLite database
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def create_test_client(db_session):
    def _create(name: str, tier: str = "basic", secret: str = "secret123") -> Client:
        client = Client(
            name=name,
            tier=tier,
            jwt_secret=hash_secret(secret),
        )
        db_session.add(client)
        db_session.commit()
        db_session.refresh(client)
        return client

    return _create


@pytest.fixture
def auth_headers(create_test_client):
    def _headers(name: str = "testuser", tier: str = "basic", secret: str = "secret123"):
        client = create_test_client(name=name, tier=tier, secret=secret)
        token = create_access_token(
            data={"sub": str(client.id), "name": client.name, "tier": client.tier},
            secret_key="test-secret-key-12345",
        )
        return {"Authorization": f"Bearer {token}"}

    return _headers

