import logging
from fastapi import APIRouter, HTTPException, Request

from orders import from_tradingview
from smartapi_wrapper import get_wrapper

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhook")
async def tradingview_webhook(payload: Request):
    try:
        data = await payload.json()
    except Exception as exc:
        logger.error("Invalid payload: %s", exc)
        raise HTTPException(status_code=400, detail="invalid payload")

    wrapper = get_wrapper()
    order_params = from_tradingview(data)
    try:
        resp = wrapper.place_order(order_params)
    except Exception as exc:
        logger.exception("Failed to place order: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))
    return {"status": "order_sent", "response": resp}
