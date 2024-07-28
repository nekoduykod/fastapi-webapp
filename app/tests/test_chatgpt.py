import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_gpt_page():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/chatgpt")
        assert response.status_code == 200
        assert "chatgpt" in response.text.lower()


# @pytest.mark.asyncio
# async def test_chat_with_gpt():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post("/chatgpt", data={"message": "Hello, GPT!"})
#         assert response.status_code == 200
#         assert "generated_message" in response.text.lower()
