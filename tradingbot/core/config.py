"""Application configuration using Pydantic settings."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # SmartAPI Configuration
    smartapi_api_key: str = Field(..., description="SmartAPI API key")
    smartapi_client_code: str = Field(..., description="SmartAPI client code")
    smartapi_password: str = Field(..., description="SmartAPI password")
    smartapi_totp: str = Field(..., description="SmartAPI TOTP secret")
    
    # Google Cloud Storage
    gcs_bucket: Optional[str] = Field(None, description="GCS bucket for token storage")
    google_application_credentials: Optional[str] = Field(
        None, description="Path to GCP service account key"
    )
    
    # Redis Configuration
    redis_host: str = Field("localhost", description="Redis host")
    redis_port: int = Field(6379, description="Redis port")
    redis_db: int = Field(0, description="Redis database")
    redis_password: Optional[str] = Field(None, description="Redis password")
    
    # Application Configuration
    app_name: str = Field("TradingBot SmartAPI", description="Application name")
    debug: bool = Field(False, description="Debug mode")
    log_level: str = Field("INFO", description="Logging level")
    
    # API Configuration
    api_host: str = Field("0.0.0.0", description="API host")
    api_port: int = Field(8080, description="API port")
    api_workers: int = Field(1, description="Number of API workers")
    
    # Trading Configuration
    max_order_retries: int = Field(3, description="Maximum order retry attempts")
    websocket_reconnect_delay: int = Field(5, description="WebSocket reconnect delay in seconds")
    position_sync_interval: int = Field(60, description="Position sync interval in seconds")


# Global settings instance
settings = Settings()