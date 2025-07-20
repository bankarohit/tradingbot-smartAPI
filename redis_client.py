import os
import redis

_redis_client = None


def get_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        db = int(os.getenv("REDIS_DB", 0))
        _redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
    return _redis_client


def set_position(symbol: str, qty: int) -> None:
    get_client().set(symbol, qty)


def get_position(symbol: str) -> int:
    val = get_client().get(symbol)
    return int(val) if val is not None else 0


def update_position(symbol: str, qty_delta: int) -> int:
    current = get_position(symbol)
    new_qty = current + qty_delta
    set_position(symbol, new_qty)
    return new_qty
