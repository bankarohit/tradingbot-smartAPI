from typing import Any, Dict


def from_tradingview(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert TradingView webhook payload to SmartAPI order parameters."""
    return {
        "variety": data.get("variety", "NORMAL"),
        "tradingsymbol": data["symbol"],
        "symboltoken": data.get("token"),
        "transactiontype": data.get("side", "BUY"),
        "exchange": data.get("exchange", "NSE"),
        "ordertype": data.get("order_type", "MARKET"),
        "producttype": data.get("product_type", "INTRADAY"),
        "duration": data.get("duration", "DAY"),
        "price": data.get("price"),
        "squareoff": data.get("squareoff"),
        "stoploss": data.get("stoploss"),
        "quantity": int(data.get("qty", 1)),
    }
