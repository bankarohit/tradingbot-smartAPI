"""Position management endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from tradingbot.models.orders import Position
from tradingbot.services.smartapi_client import SmartAPIClient
from tradingbot.api.dependencies import get_client

router = APIRouter(prefix="/positions", tags=["positions"])


@router.get("/", response_model=List[Position])
async def get_positions(client: SmartAPIClient = Depends(get_client)):
    """Get all current positions."""
    try:
        result = await client.get_positions()
        return result.get("positions", [])
    except Exception as e:
        logger.error(f"Failed to get positions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve positions"
        )


@router.get("/{symbol}", response_model=Position)
async def get_position(symbol: str, client: SmartAPIClient = Depends(get_client)):
    """Get position for a specific symbol."""
    try:
        position = await client.position_manager.get_position(symbol)
        return position
    except Exception as e:
        logger.error(f"Failed to get position for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve position for {symbol}"
        )


@router.delete("/{symbol}")
async def clear_position(symbol: str, client: SmartAPIClient = Depends(get_client)):
    """Clear position for a specific symbol."""
    try:
        await client.position_manager.clear_position(symbol)
        return {"status": "success", "message": f"Position cleared for {symbol}"}
    except Exception as e:
        logger.error(f"Failed to clear position for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear position for {symbol}"
        )


@router.delete("/")
async def clear_all_positions(client: SmartAPIClient = Depends(get_client)):
    """Clear all positions."""
    try:
        await client.position_manager.clear_all_positions()
        return {"status": "success", "message": "All positions cleared"}
    except Exception as e:
        logger.error(f"Failed to clear all positions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear all positions"
        )