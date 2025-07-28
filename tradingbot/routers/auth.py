from fastapi import APIRouter, HTTPException
import logging

from tradingbot.services.smartapi_wrapper import get_wrapper

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login")
async def login():
    wrapper = get_wrapper()
    session = wrapper.login()
    if "error" in session:
        logger.error("Login failed: %s", session["error"])
        raise HTTPException(status_code=502, detail=session["error"])
    return {"status": "success", "data": session["data"]}


@router.post("/logout")
async def logout():
    wrapper = get_wrapper()
    wrapper.logout()
    return {"status": "logged out"}
