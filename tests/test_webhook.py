from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_hello_world_get():
    response = client.get("/webhook")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_hello_world_post():
    response = client.post("/webhook")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
