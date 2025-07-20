# tradingbot-smartAPI

This project exposes a FastAPI service for receiving TradingView webhooks and placing orders through Angel One's SmartAPI. Tokens are stored in Google Cloud Storage and open positions are tracked in Redis. Order updates are listened to over a WebSocket connection.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Set the following environment variables:

- `SMARTAPI_API_KEY`
- `SMARTAPI_CLIENT_CODE`
- `SMARTAPI_PASSWORD`
- `SMARTAPI_TOTP`
- `GCS_BUCKET` – Google Cloud Storage bucket name for persisting session tokens
- `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB`

Ensure Google Cloud credentials are available (e.g. `GOOGLE_APPLICATION_CREDENTIALS`).

## Running

```bash
uvicorn main:app --reload
```

Endpoints:

- `POST /auth/login` – authenticate with SmartAPI
- `POST /auth/logout` – logout and clear session
- `POST /webhook` – TradingView webhook endpoint
