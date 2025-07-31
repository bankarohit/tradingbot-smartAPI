"""Webhook endpoints for TradingView integration."""

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from tradingbot.models.orders import TradingViewWebhook, OrderResponse
from tradingbot.services.smartapi_client import SmartAPIClient
from tradingbot.api.dependencies import get_client
from tradingbot.core.exceptions import OrderError, AuthenticationError

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/tradingview", response_model=OrderResponse)
async def tradingview_webhook(
    webhook: TradingViewWebhook,
    client: SmartAPIClient = Depends(get_client)
) -> OrderResponse:
    """Process TradingView webhook and place order."""
    try:
        logger.info(f"Received TradingView webhook: {webhook.model_dump()}")
        
        # Place order
        response = await client.place_order(webhook)
        
        logger.info(f"Order processed successfully: {response.model_dump()}")
        return response
        
    except OrderError as e:
        logger.error(f"Order failed: {e.message}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": e.message,
                "error_code": e.error_code,
                "details": e.details
            }
        )
    except AuthenticationError as e:
        logger.error(f"Authentication failed during order: {e.message}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": e.message,
                "error_code": e.error_code
            }
        )
    except Exception as e:
        logger.error(f"Unexpected webhook error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Webhook processing failed"
        )


@router.get("/test")
async def test_webhook():
    """Test webhook endpoint."""
    return {
        "status": "ok",
        "message": "Webhook endpoint is working",
        "example_payload": {
            "symbol": "SBIN-EQ",
            "side": "BUY",
            "qty": 1,
            "order_type": "MARKET",
            "product_type": "INTRADAY",
            "exchange": "NSE"
        }
    }