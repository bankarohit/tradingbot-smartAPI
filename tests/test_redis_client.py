import redis_client

class DummyRedis:
    def __init__(self, *args, **kwargs):
        self.store = {}
    def set(self, key, value):
        self.store[key] = value
    def get(self, key):
        return self.store.get(key)


def setup_dummy(monkeypatch):
    dummy = DummyRedis()
    monkeypatch.setattr(redis_client, '_redis_client', None)
    monkeypatch.setattr(redis_client.redis, 'Redis', lambda host, port, db, decode_responses=True: dummy)
    return dummy


def test_set_and_get_position(monkeypatch):
    dummy = setup_dummy(monkeypatch)
    redis_client.set_position('SBIN-EQ', 2)
    assert redis_client.get_position('SBIN-EQ') == 2
    assert dummy.store['SBIN-EQ'] == 2
    assert redis_client.get_position('NON') == 0


def test_update_position(monkeypatch):
    dummy = setup_dummy(monkeypatch)
    redis_client.set_position('SBIN-EQ', 2)
    new_qty = redis_client.update_position('SBIN-EQ', 3)
    assert new_qty == 5
    assert redis_client.get_position('SBIN-EQ') == 5
