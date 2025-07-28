import logging
import asyncio

from fastapi import FastAPI

from tradingbot.utils import logging_config
from tradingbot.routers.auth import router as auth_router
from tradingbot.services.smartapi_wrapper import get_wrapper
from tradingbot.routers.webhook import router as webhook_router

logging_config.setup_logging()

app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(webhook_router)


logger = logging.getLogger(__name__)


@app.on_event("startup")
async def start_websocket():
    wrapper = get_wrapper()
    attempts = 3
    for attempt in range(1, attempts + 1):
        try:
            wrapper.start_websocket(wrapper.default_update_handler)
            break
        except Exception as exc:
            logger.exception(
                "WebSocket start failed (attempt %s/%s): %s",
                attempt,
                attempts,
                exc,
            )
            if attempt < attempts:
                await asyncio.sleep(2)
    else:
        logger.error("Could not establish WebSocket connection")
