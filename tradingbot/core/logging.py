"""Enhanced logging configuration with structured logging."""

import sys
from typing import Any, Dict
from loguru import logger
from tradingbot.core.config import settings


class InterceptHandler:
    """Intercept standard logging and redirect to loguru."""
    
    def emit(self, record: Any) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename.startswith("<"):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """Configure structured logging with loguru."""
    
    # Remove default handler
    logger.remove()
    
    # Add structured JSON logging for production
    if not settings.debug:
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level=settings.log_level,
            serialize=True,
            backtrace=True,
            diagnose=True,
        )
    else:
        # Pretty logging for development
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
            level=settings.log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
    
    # Intercept standard library logging
    import logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("uvicorn.error").disabled = True
    
    logger.info("Logging configured", level=settings.log_level, debug=settings.debug)