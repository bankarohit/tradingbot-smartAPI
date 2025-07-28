import logging
import pytest

from tradingbot.services import smartapi_wrapper


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


def test_place_order_returns_login_error(monkeypatch, caplog):
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    monkeypatch.setattr(wrapper, "login", lambda: {"error": "bad"})

    with caplog.at_level(logging.ERROR):
        resp = wrapper.place_order({"k": "v"})

    assert resp == {"error": "bad"}
    assert any("Login failed" in r.message for r in caplog.records)


def test_default_update_handler_buy_and_sell(monkeypatch):
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    calls = []
    monkeypatch.setattr('tradingbot.services.smartapi_wrapper.update_position', lambda sym, qty: calls.append((sym, qty)))

    buy_msg = '{"tradingsymbol":"SBIN-EQ","quantity":"2","transactiontype":"BUY"}'
    sell_msg = '{"tradingsymbol":"SBIN-EQ","quantity":"1","transactiontype":"SELL"}'

    wrapper.default_update_handler(buy_msg)
    wrapper.default_update_handler(sell_msg)

    assert calls == [("SBIN-EQ", 2), ("SBIN-EQ", -1)]


def test_default_update_handler_error_logged(monkeypatch, caplog):
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    monkeypatch.setattr('tradingbot.services.smartapi_wrapper.update_position', lambda *a, **k: 1)

    with caplog.at_level(logging.ERROR):
        wrapper.default_update_handler("not json")

    assert any("Failed to process order update" in r.message for r in caplog.records)


class DummyBlob:
    def __init__(self):
        self.data = None
    def upload_from_string(self, data):
        self.data = data
    def download_as_bytes(self):
        return self.data.encode()
    def exists(self):
        return self.data is not None


class DummyBucket:
    def __init__(self):
        self.blob_obj = DummyBlob()
    def blob(self, name):
        return self.blob_obj


class DummyClient:
    def __init__(self):
        self.bucket_obj = DummyBucket()
    def bucket(self, name):
        return self.bucket_obj


def test_save_and_load_token(monkeypatch):
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    wrapper.gcs_bucket_name = 'b'
    client = DummyClient()
    monkeypatch.setattr(smartapi_wrapper.storage, 'Client', lambda: client)

    token = {'data': {'jwtToken': 't'}}
    wrapper._save_token(token)
    loaded = wrapper._load_token()
    assert loaded == token


def test_logout_logs_error(monkeypatch, caplog):
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    class BadSmart:
        def logout(self):
            raise Exception('fail')
    wrapper.smart = BadSmart()
    with caplog.at_level(logging.ERROR):
        wrapper.logout()
    assert any('Logout failed' in r.message for r in caplog.records)
    assert wrapper.session is None


class DummyThread:
    def __init__(self, target=None, args=(), daemon=None):
        self.target = target
        self.args = args
        self.daemon = daemon
        self.started = False
    def start(self):
        self.started = True
        if self.target:
            self.target(*self.args)
    def is_alive(self):
        return self.started


def test_start_websocket_starts_thread(monkeypatch):
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    wrapper.smart = object()
    wrapper.session = {'data': {'feedToken': 'f', 'jwtToken': 'j'}}
    monkeypatch.setattr(smartapi_wrapper, 'Thread', DummyThread)
    called = {}
    monkeypatch.setattr(wrapper, '_run_ws', lambda cb: called.setdefault('run', True))
    wrapper.start_websocket(lambda x: None)
    assert called.get('run')
    assert isinstance(wrapper.ws_thread, DummyThread) and wrapper.ws_thread.started


def test_start_websocket_sets_websocket(monkeypatch):
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    wrapper.smart = object()
    wrapper.session = {'data': {'feedToken': 'f', 'jwtToken': 'j'}}
    monkeypatch.setattr(smartapi_wrapper, 'Thread', DummyThread)

    class DummyWS:
        def __init__(self, *args, **kwargs):
            self.connected = False
            self.closed = False
            self.on_message = None
        def connect(self):
            self.connected = True
        def close_connection(self):
            self.closed = True

    monkeypatch.setattr(smartapi_wrapper, 'SmartWebSocketOrderUpdate', DummyWS)

    wrapper.start_websocket(lambda x: None)

    assert isinstance(wrapper.websocket, DummyWS)
    assert wrapper.websocket.connected


def test_stop_websocket_clears_state(monkeypatch):
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    wrapper.smart = object()
    wrapper.session = {'data': {'feedToken': 'f', 'jwtToken': 'j'}}
    monkeypatch.setattr(smartapi_wrapper, 'Thread', DummyThread)

    class DummyWS:
        def __init__(self, *args, **kwargs):
            self.closed = False
        def connect(self):
            pass
        def close_connection(self):
            self.closed = True

    monkeypatch.setattr(smartapi_wrapper, 'SmartWebSocketOrderUpdate', DummyWS)

    wrapper.start_websocket(lambda x: None)

    ws = wrapper.websocket
    assert wrapper.ws_thread is not None

    wrapper.stop_websocket()

    assert ws.closed
    assert wrapper.websocket is None
    assert wrapper.ws_thread is None


def test_start_websocket_login_failure(monkeypatch, caplog):
    wrapper = smartapi_wrapper.SmartAPIWrapper()
    monkeypatch.setattr(smartapi_wrapper, 'Thread', DummyThread)
    monkeypatch.setattr(wrapper, 'login', lambda: {'error': 'fail'})
    called = {}
    monkeypatch.setattr(wrapper, '_run_ws', lambda cb: called.setdefault('run', True))

    with caplog.at_level(logging.ERROR):
        wrapper.start_websocket(lambda x: None)

    assert 'run' not in called
    assert wrapper.ws_thread is None
    assert any('Login failed' in r.message for r in caplog.records)
