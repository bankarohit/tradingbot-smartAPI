import json
import logging
import os
from threading import Thread
from typing import Any, Callable, Dict, Optional

from google.cloud import storage
from SmartApi import SmartConnect
from SmartApi.smartWebSocketOrderUpdate import SmartWebSocketOrderUpdate

from tradingbot.services.redis_client import update_position

logger = logging.getLogger(__name__)


class SmartAPIWrapper:
    """Wrapper around SmartConnect handling token storage and order updates."""

    def __init__(self) -> None:
        self.api_key = os.getenv("SMARTAPI_API_KEY")
        self.client_code = os.getenv("SMARTAPI_CLIENT_CODE")
        self.password = os.getenv("SMARTAPI_PASSWORD")
        self.totp = os.getenv("SMARTAPI_TOTP")
        self.gcs_bucket_name = os.getenv("GCS_BUCKET")
        self.token_file = "smartapi_token.json"
        self.smart: Optional[SmartConnect] = None
        self.session: Optional[Dict[str, Any]] = None
        self.ws_thread: Optional[Thread] = None
        self.websocket = None

    # Google Cloud Storage helpers
    def _bucket(self) -> storage.bucket.Bucket:
        client = storage.Client()
        return client.bucket(self.gcs_bucket_name)

    def _save_token(self, token: Dict[str, Any]) -> None:
        if not self.gcs_bucket_name:
            return
        blob = self._bucket().blob(self.token_file)
        blob.upload_from_string(json.dumps(token))
        logger.info("Stored token to GCS")

    def _load_token(self) -> Optional[Dict[str, Any]]:
        if not self.gcs_bucket_name:
            return None
        blob = self._bucket().blob(self.token_file)
        if blob.exists():
            data = blob.download_as_bytes()
            return json.loads(data.decode())
        return None

    # Authentication
    def login(self) -> Dict[str, Any]:
        """Authenticate with SmartAPI and persist the session token."""
        try:
            self.smart = SmartConnect(api_key=self.api_key)

            try:
                token = self._load_token()
            except Exception as exc:  # GCS errors
                logger.exception("Failed to load token: %s", exc)
                token = None

            if token:
                self.smart.set_session(token["data"]["jwtToken"])
                self.session = token
                logger.info("Loaded SmartAPI session from storage")
                return token

            session = self.smart.generateSession(
                self.client_code, self.password, self.totp
            )
            self.session = session
            try:
                self._save_token(session)
            except Exception as exc:  # GCS errors
                logger.exception("Failed to save token: %s", exc)
            logger.info("Generated new SmartAPI session")
            return session
        except Exception as exc:
            logger.exception("Failed to login to SmartAPI: %s", exc)
            return {"error": str(exc)}

    def logout(self) -> None:
        if self.smart:
            try:
                self.smart.logout()
            except Exception as exc:
                logger.error("Logout failed: %s", exc)
        self.session = None

    # Orders
    def place_order(self, params: Dict[str, Any]) -> Any:
        if not self.smart or not self.session:
            login_res = self.login()
            if isinstance(login_res, dict) and "error" in login_res:
                logger.error("Login failed: %s", login_res["error"])
                return login_res

        if not self.smart or not self.session:
            logger.error("SmartAPI session not established")
            return {"error": "login failed"}

        try:
            resp = self.smart.placeOrder(params)
        except Exception as exc:
            logger.exception("Failed to place order: %s", exc)
            return {"error": str(exc)}
        logger.info("Order response: %s", resp)
        return resp

    # Websocket
    def _run_ws(self, on_update: Callable[[str], None]) -> None:
        token = self.session["data"]["feedToken"]
        jwt = self.session["data"]["jwtToken"]
        ws = SmartWebSocketOrderUpdate(jwt, self.api_key, self.client_code, token)
        ws.on_message = lambda wsapp, msg: on_update(msg)
        ws.connect()

    def start_websocket(self, on_update: Callable[[str], None]) -> None:
        if not self.smart or not self.session:
            self.login()
        if self.ws_thread and self.ws_thread.is_alive():
            return
        self.ws_thread = Thread(target=self._run_ws, args=(on_update,), daemon=True)
        self.ws_thread.start()

    def default_update_handler(self, message: str) -> None:
        """Handle order update messages and track positions in Redis."""
        logger.info("Order update: %s", message)
        try:
            data = json.loads(message)
            symbol = data.get("tradingsymbol") or data.get("symboltoken")
            qty = int(data.get("quantity", 0))
            txn = data.get("transactiontype")
            if symbol and qty:
                if txn == "BUY":
                    update_position(symbol, qty)
                elif txn == "SELL":
                    update_position(symbol, -qty)
        except Exception as exc:
            logger.error("Failed to process order update: %s", exc)


_wrapper: Optional[SmartAPIWrapper] = None


def get_wrapper() -> SmartAPIWrapper:
    global _wrapper
    if _wrapper is None:
        _wrapper = SmartAPIWrapper()
    return _wrapper
