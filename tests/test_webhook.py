import logging
import pytest
from fastapi.testclient import TestClient

import tradingbot.main as main


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


class FailingWrapper(DummyWrapper):
    def place_order(self, params):
        raise Exception("boom")


class ErrorWrapper(DummyWrapper):
    def place_order(self, params):
        return {"error": "bad"}


@pytest.fixture
def client(monkeypatch):
    wrapper = DummyWrapper()
    monkeypatch.setattr(
        "tradingbot.services.smartapi_wrapper.get_wrapper", lambda: wrapper
    )
    monkeypatch.setattr(main, "get_wrapper", lambda: wrapper)
    from tradingbot.routers import webhook

    monkeypatch.setattr(webhook, "get_wrapper", lambda: wrapper)
    app = main.app
    return TestClient(app)


@pytest.fixture
def failing_client(monkeypatch):
    wrapper = FailingWrapper()
    monkeypatch.setattr(
        "tradingbot.services.smartapi_wrapper.get_wrapper", lambda: wrapper
    )
    monkeypatch.setattr(main, "get_wrapper", lambda: wrapper)
    from tradingbot.routers import webhook

    monkeypatch.setattr(webhook, "get_wrapper", lambda: wrapper)
    app = main.app
    return TestClient(app)


@pytest.fixture
def error_client(monkeypatch):
    wrapper = ErrorWrapper()
    monkeypatch.setattr(
        "tradingbot.services.smartapi_wrapper.get_wrapper", lambda: wrapper
    )
    monkeypatch.setattr(main, "get_wrapper", lambda: wrapper)
    from tradingbot.routers import webhook

    monkeypatch.setattr(webhook, "get_wrapper", lambda: wrapper)
    app = main.app
    return TestClient(app)


@pytest.fixture
def exception_client(monkeypatch):
    wrapper = DummyWrapper()
    monkeypatch.setattr(
        "tradingbot.services.smartapi_wrapper.get_wrapper", lambda: wrapper
    )
    monkeypatch.setattr(main, "get_wrapper", lambda: wrapper)
    from tradingbot.routers import webhook

    monkeypatch.setattr(webhook, "get_wrapper", lambda: wrapper)
    app = main.app
    return TestClient(app, raise_server_exceptions=False)


def test_webhook_invalid_json(client):
    response = client.post(
        "/webhook", data="notjson", headers={"Content-Type": "application/json"}
    )
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


def test_webhook_order_failure(failing_client, caplog):
    payload = {"symbol": "SBIN-EQ", "qty": 1}
    with caplog.at_level(logging.ERROR):
        response = failing_client.post("/webhook", json=payload)
    assert response.status_code == 502
    assert any("Failed to place order" in r.message for r in caplog.records)


def test_webhook_order_error_dict(error_client, caplog):
    payload = {"symbol": "SBIN-EQ", "qty": 1}
    with caplog.at_level(logging.ERROR):
        response = error_client.post("/webhook", json=payload)
    assert response.status_code == 502
    assert any("Order error" in r.message for r in caplog.records)

class MissingSymbolWrapper(DummyWrapper):
    def place_order(self, params):
        return super().place_order(params)


def test_webhook_missing_symbol(exception_client):
    response = exception_client.post("/webhook", json={"qty": 1})
    # from_tradingview will raise KeyError leading to 500 response
    assert response.status_code == 500

