import pytest
from fastapi.testclient import TestClient
import main

class DummyWrapper:
    def __init__(self):
        self.logged_in = False
        self.logged_out = False
    def login(self):
        self.logged_in = True
        return {"data": {"jwtToken": "t"}}
    def logout(self):
        self.logged_out = True

@pytest.fixture
def auth_client(monkeypatch):
    wrapper = DummyWrapper()
    monkeypatch.setattr("smartapi_wrapper.get_wrapper", lambda: wrapper)
    import auth
    monkeypatch.setattr(auth, "get_wrapper", lambda: wrapper)
    monkeypatch.setattr(main, "get_wrapper", lambda: wrapper)
    app = main.app
    return TestClient(app)


def test_login_endpoint(auth_client):
    resp = auth_client.post("/auth/login")
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"


def test_logout_endpoint(auth_client):
    resp = auth_client.post("/auth/logout")
    assert resp.status_code == 200
    assert resp.json()["status"] == "logged out"
