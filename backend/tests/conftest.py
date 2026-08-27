"""
pytest configuration and shared fixtures.

Uses SQLite in-memory (via file path for multi-connection support) so tests
run without a live PostgreSQL server.  The database is created fresh for
each test session and destroyed after.

Fixtures available:
  db_engine    — the test SQLAlchemy engine (session-scoped)
  db           — a transactional database session (function-scoped, rolled back)
  client       — FastAPI TestClient with DB dependency overridden
  auth_headers — Authorization header for a pre-registered test user
"""

import os
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Use a file-based SQLite DB so multiple in-process connections see the same data.
TEST_DB_PATH = "./test_qcommerce.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"


@pytest.fixture(scope="session")
def db_engine():
    """Create all tables once for the test session."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

    # Enable WAL mode and foreign key enforcement for SQLite.
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    from app.core.database import Base
    import app.models  # noqa: F401 — register all 16 models

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    # Clean up the SQLite file.
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    wal = TEST_DB_PATH + "-wal"
    shm = TEST_DB_PATH + "-shm"
    for f in (wal, shm):
        if os.path.exists(f):
            os.remove(f)


@pytest.fixture(scope="function")
def db(db_engine):
    """
    Yield a database session that is rolled back after each test.

    Using SAVEPOINT / nested transactions keeps each test isolated without
    recreating the schema.
    """
    connection = db_engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    """
    FastAPI TestClient with the `get_db` dependency overridden to use the
    test session so every request shares the same transactional context.
    """
    from app.main import app
    from app.core.database import get_db

    def override_get_db():
        try:
            yield db
        finally:
            pass  # rollback handled by `db` fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client):
    """Register + login a test user and return Authorization headers."""
    resp = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123",
        "full_name": "Test User",
        "retailer_name": "TestRetailer",
    })
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
