"""FastAPI dependencies."""

from typing import AsyncGenerator
from tradingbot.services.smartapi_client import SmartAPIClient, get_smartapi_client


async def get_client() -> AsyncGenerator[SmartAPIClient, None]:
    """Dependency to get SmartAPI client."""
    client = get_smartapi_client()
    try:
        yield client
    finally:
        # Cleanup if needed
        pass