import asyncio
import logging
import tradingbot.main as main
from tradingbot.services import smartapi_wrapper

class FailingWrapper:
    def __init__(self):
        self.calls = 0
    def start_websocket(self, handler):
        self.calls += 1
        raise Exception('boom')
    def default_update_handler(self, msg):
        pass


def test_startup_websocket_failure_logged(monkeypatch, caplog):
    wrapper = FailingWrapper()
    monkeypatch.setattr(smartapi_wrapper, 'get_wrapper', lambda: wrapper)
    monkeypatch.setattr(main, 'get_wrapper', lambda: wrapper)

    with caplog.at_level(logging.ERROR):
        asyncio.run(main.start_websocket())

    assert wrapper.calls >= 1
    assert any('WebSocket start failed' in r.message for r in caplog.records)
