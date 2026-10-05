import io
import os
import shutil
from pathlib import Path
from typing import Generator
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import get_settings
from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.waste_report import WasteReport
from app.models.collection_request import CollectionRequest
from app.utils.security import get_password_hash, create_access_token

TEST_DB_FILE = Path(__file__).parent / "test_waste_management.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE.resolve()}"
TEST_UPLOAD_DIR = Path(__file__).parent / "test_uploads"

# Create isolated test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Enforce foreign key constraints on SQLite test database
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Session fixture to create isolated test database and upload directory."""
    # Ensure previous test artifacts are clean
    if TEST_DB_FILE.exists():
        TEST_DB_FILE.unlink()
    if TEST_UPLOAD_DIR.exists():
        shutil.rmtree(TEST_UPLOAD_DIR)
    TEST_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Point settings to test upload directory
    settings = get_settings()
    original_upload_dir = settings.UPLOAD_DIR
    settings.UPLOAD_DIR = str(TEST_UPLOAD_DIR.name)

    # Create tables in test database
    Base.metadata.create_all(bind=test_engine)

    yield

    # Teardown: drop tables, remove test database and upload files
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except Exception:
            pass
    if TEST_UPLOAD_DIR.exists():
        shutil.rmtree(TEST_UPLOAD_DIR, ignore_errors=True)
    settings.UPLOAD_DIR = original_upload_dir


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Function-scoped clean database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        # Clean up table rows between tests to ensure complete isolation
        session.query(CollectionRequest).delete()
        session.query(WasteReport).delete()
        session.query(User).delete()
        session.commit()
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with isolated test database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def normal_user(db_session: Session):
    """Creates a regular test user and returns auth metadata."""
    user = User(
        name="Test Regular User",
        email="regular@ecocycle.test",
        password_hash=get_password_hash("Password123!"),
        role=UserRole.USER.value,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    return {
        "user": user,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def second_user(db_session: Session):
    """Creates a second distinct regular user for cross-user authorization tests."""
    user = User(
        name="Second Test User",
        email="second@ecocycle.test",
        password_hash=get_password_hash("Password123!"),
        role=UserRole.USER.value,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    return {
        "user": user,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def admin_user(db_session: Session):
    """Creates an administrator user and returns auth metadata."""
    admin = User(
        name="Test Admin User",
        email="admin@ecocycle.test",
        password_hash=get_password_hash("Admin123!"),
        role=UserRole.ADMIN.value,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    token = create_access_token({"sub": str(admin.id), "email": admin.email, "role": admin.role})
    return {
        "user": admin,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


def make_test_image(format="JPEG", color=(34, 139, 34), size=(100, 100)) -> bytes:
    """Helper to generate binary image payloads in memory."""
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()
