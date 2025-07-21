import logging
import pytest

import smartapi_wrapper


class DummySmart:
    def __init__(self, *args, **kwargs):
        self.session_set = None
        self.generated = False
        self.ordered = None

    def set_session(self, token):
        self.session_set = token

    def generateSession(self, client_code, password, totp):
        self.generated = True
        return {"data": {"jwtToken": "jwt", "feedToken": "feed"}}

    def placeOrder(self, params):
        self.ordered = params
        return {"order": "ok"}

    def logout(self):
        pass


def test_login_uses_stored_token(monkeypatch):
    token = {"data": {"jwtToken": "t1", "feedToken": "f1"}}
    monkeypatch.setattr(smartapi_wrapper, "SmartConnect", DummySmart)
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    monkeypatch.setattr(wrapper, "_load_token", lambda: token)
    called = {}
    monkeypatch.setattr(wrapper, "_save_token", lambda t: called.setdefault("saved", t))

    session = wrapper.login()
    assert session == token
    assert wrapper.smart.session_set == "t1"
    assert "saved" not in called


def test_login_generates_token(monkeypatch):
    monkeypatch.setattr(smartapi_wrapper, "SmartConnect", DummySmart)
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    monkeypatch.setattr(wrapper, "_load_token", lambda: None)
    saved = {}
    monkeypatch.setattr(wrapper, "_save_token", lambda t: saved.setdefault("token", t))

    session = wrapper.login()
    assert wrapper.smart.generated
    assert saved["token"] == session
    assert wrapper.session == session


def test_place_order_triggers_login(monkeypatch):
    monkeypatch.setattr(smartapi_wrapper, "SmartConnect", DummySmart)
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    monkeypatch.setattr(
        wrapper, "_load_token", lambda: {"data": {"jwtToken": "t", "feedToken": "f"}}
    )
    monkeypatch.setattr(wrapper, "_save_token", lambda t: None)

    resp = wrapper.place_order({"key": "val"})
    assert wrapper.session is not None  # login was called
    assert wrapper.smart.ordered == {"key": "val"}
    assert resp == {"order": "ok"}


def test_place_order_logs_and_returns_error(monkeypatch, caplog):
    monkeypatch.setattr(smartapi_wrapper, "SmartConnect", DummySmart)
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    monkeypatch.setattr(
        wrapper,
        "_load_token",
        lambda: {"data": {"jwtToken": "t", "feedToken": "f"}},
    )
    monkeypatch.setattr(wrapper, "_save_token", lambda t: None)

    def raise_order(self, params):
        raise Exception("boom")

    monkeypatch.setattr(DummySmart, "placeOrder", raise_order)

    with caplog.at_level(logging.ERROR):
        resp = wrapper.place_order({"k": "v"})

    assert resp == {"error": "boom"}
    assert any("Failed to place order" in r.message for r in caplog.records)


def test_login_logs_load_token_failure(monkeypatch, caplog):
    monkeypatch.setattr(smartapi_wrapper, "SmartConnect", DummySmart)
    wrapper = smartapi_wrapper.SmartAPIWrapper()

    def fail_load():
        raise Exception("gcs boom")

    monkeypatch.setattr(wrapper, "_load_token", fail_load)
    monkeypatch.setattr(wrapper, "_save_token", lambda t: None)

    with caplog.at_level(logging.ERROR):
        session = wrapper.login()

    assert wrapper.smart.generated
    assert session.get("data")
    assert any("Failed to load token" in r.message for r in caplog.records)


def test_login_logs_save_token_failure(monkeypatch, caplog):
    monkeypatch.setattr(smartapi_wrapper, "SmartConnect", DummySmart)
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    monkeypatch.setattr(wrapper, "_load_token", lambda: None)

    def fail_save(token):
        raise Exception("gcs save boom")

    monkeypatch.setattr(wrapper, "_save_token", fail_save)

    with caplog.at_level(logging.ERROR):
        session = wrapper.login()

    assert wrapper.smart.generated
    assert session.get("data")
    assert any("Failed to save token" in r.message for r in caplog.records)


class FailingSmart:
    def __init__(self, *args, **kwargs):
        raise Exception("connect boom")


def test_login_returns_error_on_smartconnect_failure(monkeypatch, caplog):
    monkeypatch.setattr(smartapi_wrapper, "SmartConnect", FailingSmart)
    wrapper = smartapi_wrapper.SmartAPIWrapper()

    with caplog.at_level(logging.ERROR):
        resp = wrapper.login()

    assert resp == {"error": "connect boom"}
    assert any("Failed to login to SmartAPI" in r.message for r in caplog.records)
