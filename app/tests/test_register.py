import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_register_page():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/register")
        assert response.status_code == 200
        assert "register" in response.text.lower()


@pytest.mark.asyncio
async def test_register_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/register", data={"username": "newuser", "password": "newpass", "email": "new@example.com"})
        assert response.status_code == 200  



@pytest.mark.asyncio
async def test_register_existing_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/register", data={"username": "test1", "password": "test1", "email": "test1@example.com"})
        assert response.status_code == 200
        assert "nickname is taken. please choose another one" in response.text.lower()