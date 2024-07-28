import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers, Session
from fastapi import Request
from typing import Generator

from app.main import app
from app.models.models import Base, Users as ModelUsers, pwd_context


TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, echo=True)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_session(request: Request):
    return {"user": {"username": "testuser"}}


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
    clear_mappers()

@pytest.fixture(scope="function")
def override_get_db(db_session: Session) -> Generator[None, None, None]:

    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides[get_db] = None

@pytest.fixture(scope="function")
def override_get_session() -> Generator[None, None, None]:

    app.dependency_overrides[get_session] = get_session
    yield
    app.dependency_overrides[get_session] = None

# Test cases
@pytest.mark.asyncio
async def test_account_page(override_get_db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/account")
        assert response.status_code == 200
        assert "account" in response.text.lower()

# @pytest.mark.asyncio
# async def test_change_pass(db_session: Session, override_get_db, override_get_session):
#     # Ensure the `Users` model is properly mapped
#     assert hasattr(ModelUsers, "__table__"), "ModelUsers is not mapped correctly."

#     # Create a test user in the database
#     test_user = ModelUsers(username="testuser", email="test@example.com")
#     test_user.set_password("oldpass")
    
#     db_session.add(test_user)
#     db_session.commit()
    
#     # Verify that the user was created
#     created_user = db_session.query(ModelUsers).filter_by(username="testuser").first()
#     assert created_user is not None, "User was not created in the database"
#     assert pwd_context.verify("oldpass", created_user.hashed_password), "Password verification failed"
    
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         # Step 1: Change the password
#         change_pass_response = await ac.post(
#             "/account",
#             data={"current_password": "oldpass", "new_password": "newpass", "confirm_password": "newpass"},
#             cookies={"session": "mocked-session-id"}  # Assuming your session middleware uses cookies
#         )

#         assert change_pass_response.status_code == 200
#         assert "password changed successfully" in change_pass_response.text.lower()

#         # Verify that the password was actually changed
#         updated_user = db_session.query(ModelUsers).filter_by(username="testuser").first()
#         assert updated_user
#         assert pwd_context.verify("newpass", updated_user.hashed_password)
    
#     # Clean up: Delete the test user from the database
#     db_session.delete(test_user)
#     db_session.commit()
