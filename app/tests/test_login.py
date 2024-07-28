import pytest
from httpx import AsyncClient
from app.main import app


pytest.mark.asyncio
async def test_login_page():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/login")
    assert response.status_code == 200
    assert "<title>Login</title>" in response.text
    assert "<h1>Login</h1>" in response.text
    assert '<input type="text" name="username"' in response.text
    assert '<input type="password" name="password"' in response.text


@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/login", data={"username": "test1", "password": "test1"})
    assert response.status_code == 303  
    assert response.headers["location"] == "/account" 

    response = await ac.get("/account")
    assert response.status_code == 200 


@pytest.mark.asyncio
async def test_login_failure():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/login", data={"username": "wronguser", "password": "wrongpass"})
    assert response.status_code == 200 
    assert "invalid login or password" in response.text.lower() 