import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "api"),
)

from app.core.security import (
    create_access_token,
    hash_password,
)
from app.db.base import Base
from app.db.database import SessionLocal
from app.main import app
from app.models.user import User
from app.models.document import Document


TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/rag_platform_test",
)


@pytest.fixture(scope="session")
def engine():

    engine = create_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
    )

    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):

    connection = engine.connect()

    transaction = connection.begin()

    session = SessionLocal(bind=connection)

    yield session

    session.close()

    transaction.rollback()

    connection.close()


@pytest.fixture(scope="function")
def client():

    with TestClient(app) as c:

        yield c


@pytest.fixture
def test_user(db_session):

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("TestPass123!"),
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def test_user_b(db_session):

    user = User(
        username="testuserb",
        email="testb@example.com",
        hashed_password=hash_password("TestPass456!"),
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def auth_headers(test_user):

    token = create_access_token(
        {
            "sub": str(test_user.id),
            "email": test_user.email,
            "tenant_id": test_user.tenant_id,
        }
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_b(test_user_b):

    token = create_access_token(
        {
            "sub": str(test_user_b.id),
            "email": test_user_b.email,
            "tenant_id": test_user_b.tenant_id,
        }
    )

    return {"Authorization": f"Bearer {token}"}
