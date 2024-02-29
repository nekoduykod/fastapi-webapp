from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():
    response = client.get(
        "/", headers = {"content-type": "text/html; charset=utf-8"})
    assert response.status_code == 200
    assert b"Simple FastAPI Web App." in response.content
    response = client.get("/static/css/styles.css")
    assert response.status_code == 200

def test_login():
   response = client.post("/login", data={"username": "testuser", "password": "testpass"})
   assert response.status_code == 200

def test_register():
   response = client.post("/register", data={"username": "newuser", "password": "newpass", "email": "newuser@example.com"})
   assert response.status_code == 200

def test_change_pass():
   response = client.post("/account", data={"current_password": "newpass", "new_password": "new2pass", "confirm_password": "new2pass"})
   assert response.status_code == 200

def test_create_shortcut():
   response = client.post("/create-shortcut", data={"shortcut_title": "test title", "shortcut_url": "http://example.com"})
   assert response.status_code == 303

def test_delete_shortcut():
   response = client.delete("/delete-shortcut/1")
   assert response.status_code == 200

def test_update_shortcuts():
   response = client.get("/update-shortcuts")
   assert response.status_code == 200

def test_go_to_shortcut():
   response = client.get("/go-to-shortcut/1")
   assert response.status_code == 200

def test_chat_with_gpt():
   response = client.post("/chatgpt", data={"message": "Hello GPT!"})
   assert response.status_code == 200