import pytest
from fastapi.testclient import TestClient

import main

class DummyWrapper:
    def __init__(self):
        self.placed = None
        self.started = False

    def place_order(self, params):
        self.placed = params
        return {"order_id": "123"}

    def start_websocket(self, handler):
        self.started = True

    def default_update_handler(self, msg):
        pass


@pytest.fixture
def client(monkeypatch):
    wrapper = DummyWrapper()
    monkeypatch.setattr("smartapi_wrapper.get_wrapper", lambda: wrapper)
    monkeypatch.setattr(main, "get_wrapper", lambda: wrapper)
    import webhook
    monkeypatch.setattr(webhook, "get_wrapper", lambda: wrapper)
    app = main.app
    return TestClient(app)


def test_webhook_invalid_json(client):
    response = client.post("/webhook", data="notjson", headers={"Content-Type": "application/json"})
    assert response.status_code == 400


def test_webhook_valid_request(client):
    payload = {"symbol": "SBIN-EQ", "qty": 1}
    response = client.post("/webhook", json=payload)
    assert response.status_code == 200
    wrapper = main.get_wrapper()
    assert wrapper.placed == {
        "variety": "NORMAL",
        "tradingsymbol": "SBIN-EQ",
        "symboltoken": None,
        "transactiontype": "BUY",
        "exchange": "NSE",
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": None,
        "squareoff": None,
        "stoploss": None,
        "quantity": 1,
    }

