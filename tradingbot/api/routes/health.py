"""Health check endpoints."""

from fastapi import APIRouter, Depends
from tradingbot.services.smartapi_client import SmartAPIClient
from tradingbot.api.dependencies import get_client

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "tradingbot-smartapi"}


@router.get("/ready")
async def readiness_check(client: SmartAPIClient = Depends(get_client)):
    """Readiness check with dependencies."""
    try:
        # Check if we can connect to Redis
        positions = await client.get_positions()
        
        return {
            "status": "ready",
            "checks": {
                "redis": "ok",
                "positions_count": positions.get("total_positions", 0)
            }
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e)
        }