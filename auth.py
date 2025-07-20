from fastapi import APIRouter

from smartapi_wrapper import get_wrapper

router = APIRouter()


@router.post("/login")
async def login():
    wrapper = get_wrapper()
    session = wrapper.login()
    return {"status": "success", "data": session.get("data")}


@router.post("/logout")
async def logout():
    wrapper = get_wrapper()
    wrapper.logout()
    return {"status": "logged out"}
