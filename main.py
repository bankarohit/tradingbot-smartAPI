import logging

from fastapi import FastAPI

import logging_config
from auth import router as auth_router
from smartapi_wrapper import get_wrapper
from webhook import router as webhook_router

logging_config.setup_logging()

app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(webhook_router)


@app.on_event("startup")
async def start_websocket():
    wrapper = get_wrapper()
    wrapper.start_websocket(wrapper.default_update_handler)
