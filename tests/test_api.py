from fastapi.testclient import TestClient
from api.app import app


client = TestClient(app)

def test_test():
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "Task submitted."}