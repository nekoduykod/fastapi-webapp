import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_shortcut():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/create-shortcut", data={"shortcut_title": "Test Shortcut", "shortcut_url": "http://example.com"})
    assert response.status_code == 303 
    assert response.headers["location"] == "/account"


@pytest.mark.asyncio
async def test_delete_shortcut():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First, create a shortcut to delete
        create_response = await ac.post("/create-shortcut", data={"shortcut_title": "Test Shortcut to Delete", "shortcut_url": "http://example.com"})
        assert create_response.status_code == 303
        # Assuming the location header is not the best way to get the created shortcut, let's fetch all shortcuts and get the id of the one we just created
        get_shortcuts_response = await ac.get("/account")
        assert get_shortcuts_response.status_code == 200
        # Assuming your response content type is JSON or similar, where you can parse the content:
        shortcuts = get_shortcuts_response.json().get("shortcuts")
        shortcut_id = next((s["id"] for s in shortcuts if s["title"] == "Test Shortcut to Delete"), None)
        assert shortcut_id is not None, "Shortcut not found in the response"

        # Now, delete the shortcut
        delete_response = await ac.post(f"/delete-shortcut/{shortcut_id}")
        assert delete_response.status_code == 200

        # Optionally, verify the shortcut is indeed deleted by fetching the list again and ensuring it's not there
        get_shortcuts_response_after_delete = await ac.get("/account")
        assert get_shortcuts_response_after_delete.status_code == 200
        shortcuts_after_delete = get_shortcuts_response_after_delete.json().get("shortcuts")
        assert all(s["id"] != shortcut_id for s in shortcuts_after_delete), "Shortcut was not deleted"

# @pytest.mark.asyncio
# async def test_go_to_shortcut():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.get("/go-to-shortcut/1")
#     assert response.status_code == 303 
