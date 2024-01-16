from fastapi.testclient import Testclient
from app.main import app

client = TestClient(app)

