"""Authentication endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from tradingbot.services.smartapi_client import SmartAPIClient
from tradingbot.api.dependencies import get_client
from tradingbot.core.exceptions import AuthenticationError

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login")
async def login(client: SmartAPIClient = Depends(get_client)):
    """Authenticate with SmartAPI."""
    try:
        session = await client.authenticate()
        logger.info("Authentication successful")
        return {
            "status": "success",
            "message": "Authentication successful",
            "data": {
                "client_code": session.get("data", {}).get("clientcode"),
                "session_active": True
            }
        }
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e.message}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": e.message,
                "error_code": e.error_code,
                "details": e.details
            }
        )
    except Exception as e:
        logger.error(f"Unexpected authentication error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Authentication service unavailable"
        )


@router.post("/logout")
async def logout(client: SmartAPIClient = Depends(get_client)):
    """Logout from SmartAPI."""
    try:
        await client.logout()
        logger.info("Logout successful")
        return {
            "status": "success",
            "message": "Logged out successfully"
        }
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Logout failed"
        )


@router.get("/status")
async def auth_status(client: SmartAPIClient = Depends(get_client)):
    """Get authentication status."""
    return {
        "authenticated": client.session is not None,
        "websocket_running": client.is_websocket_running
    }