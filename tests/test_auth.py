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


class FailingWrapper(DummyWrapper):
    def login(self):
        return {"error": "boom"}

@pytest.fixture
def auth_client(monkeypatch):
    wrapper = DummyWrapper()
    monkeypatch.setattr("smartapi_wrapper.get_wrapper", lambda: wrapper)
    import auth
    monkeypatch.setattr(auth, "get_wrapper", lambda: wrapper)
    monkeypatch.setattr(main, "get_wrapper", lambda: wrapper)
    app = main.app
    return TestClient(app)


@pytest.fixture
def failing_auth_client(monkeypatch):
    wrapper = FailingWrapper()
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


def test_login_error_returns_502(failing_auth_client):
    resp = failing_auth_client.post("/auth/login")
    assert resp.status_code == 502
    assert resp.json()["detail"] == "boom"
