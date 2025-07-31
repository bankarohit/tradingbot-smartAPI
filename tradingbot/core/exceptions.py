"""Custom exceptions for the trading bot."""

from typing import Any, Dict, Optional


class TradingBotException(Exception):
    """Base exception for trading bot errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class AuthenticationError(TradingBotException):
    """Raised when authentication fails."""
    pass


class OrderError(TradingBotException):
    """Raised when order placement fails."""
    pass


class WebSocketError(TradingBotException):
    """Raised when WebSocket connection fails."""
    pass


class ConfigurationError(TradingBotException):
    """Raised when configuration is invalid."""
    pass


class ExternalServiceError(TradingBotException):
    """Raised when external service calls fail."""
    pass