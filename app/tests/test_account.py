import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_account_page():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/account")
    assert response.status_code == 200
    assert "account" in response.text.lower()


@pytest.mark.asyncio
async def test_change_pass():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Step 1: Register a new user
        registration_response = await ac.post("/register", data={"username": "testuser", "password": "oldpass", "email": "test@example.com"})
        assert registration_response.status_code == 303  # Assuming a redirect on successful registration

        # Step 2: Log in the user
        login_response = await ac.post("/login", data={"username": "testuser", "password": "oldpass"})
        assert login_response.status_code == 303  # Assuming a redirect on successful login

        # Step 3: Change the password
        change_pass_response = await ac.post("/account", data={"current_password": "oldpass", "new_password": "newpass", "confirm_password": "newpass"})
        assert change_pass_response.status_code == 200
        assert "password changed successfully" in change_pass_response.text.lower()

        # Optionally, verify that the new password works and the old one doesn't
        # Logout or simulate a new session, then:
        logout_response = await ac.post("/logout")
        assert logout_response.status_code == 303  # Assuming a redirect on successful logout

        new_login_response = await ac.post("/login", data={"username": "testuser", "password": "newpass"})
        assert new_login_response.status_code == 303  # Should succeed with the new password

        old_login_response = await ac.post("/login", data={"username": "testuser", "password": "oldpass"})
        assert "Invalid login or password" in old_login_response.text  # Should fail with the old password
