# tradingbot-smartAPI

This project exposes a FastAPI service for receiving TradingView webhooks and placing orders through Angel One's SmartAPI. Tokens are stored in Google Cloud Storage and open positions are tracked in Redis. Order updates are listened to over a WebSocket connection.

## System Requirements

- Python 3.8 or newer
- Access to a Redis server
- Optional: Google Cloud Storage for persisting SmartAPI tokens

## Installation

Clone the repository and install dependencies in a virtual environment:

```bash
git clone <repo-url>
cd tradingbot-smartAPI
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

- `SMARTAPI_API_KEY`
- `SMARTAPI_CLIENT_CODE`
- `SMARTAPI_PASSWORD`
- `SMARTAPI_TOTP`
- `GCS_BUCKET` – Google Cloud Storage bucket name for persisting session tokens
- `REDIS_HOST` – defaults to `localhost`
- `REDIS_PORT` – defaults to `6379`
- `REDIS_DB` – defaults to `0`
- `GOOGLE_APPLICATION_CREDENTIALS` – path to your GCP service account key

## Running Locally

Start the FastAPI app. The WebSocket order update listener will automatically run on startup.

```bash
uvicorn main:app --reload
```

Endpoints:

- `POST /auth/login` – authenticate with SmartAPI
- `POST /auth/logout` – logout and clear session
- `POST /webhook` – TradingView webhook endpoint

## TradingView Alert Examples

Send JSON payloads from TradingView directly to `/webhook`. Example market order:

```json
{
  "symbol": "SBIN-EQ",
  "token": "3045",
  "side": "BUY",
  "qty": 10,
  "exchange": "NSE",
  "order_type": "MARKET",
  "product_type": "INTRADAY"
}
```

Example limit order:

```json
{
  "symbol": "SBIN-EQ",
  "side": "SELL",
  "qty": 10,
  "price": 205.5,
  "order_type": "LIMIT"
}
```

## Module Overview

- `main.py` – FastAPI application and startup hook that begins the WebSocket listener.
- `auth.py` – `/auth` routes for logging into and out of SmartAPI.
- `webhook.py` – accepts TradingView webhooks and places orders.
- `orders.py` – converts TradingView payloads to SmartAPI parameters.
- `smartapi_wrapper.py` – handles authentication, token storage and the WebSocket connection.
- `redis_client.py` – helpers for storing open positions in Redis.
- `logging_config.py` – configures JSON logging.

## Deploying to GCP

Deploy the application to Cloud Run using a container image:

```bash
gcloud builds submit --tag gcr.io/<PROJECT_ID>/tradingbot
gcloud run deploy tradingbot \
  --image gcr.io/<PROJECT_ID>/tradingbot \
  --platform managed \
  --region <REGION> \
  --set-env-vars SMARTAPI_API_KEY=...,...
```

Ensure the Cloud Run service account can access the GCS bucket storing the SmartAPI token.

## Testing

Install the dependencies and run the test suite with `pytest`:

```bash
pip install -r requirements.txt
pytest
```

## Running the WebSocket Listener Manually

The listener runs automatically when the FastAPI app starts. To run it separately:

```python
from smartapi_wrapper import get_wrapper
wrapper = get_wrapper()
wrapper.start_websocket(wrapper.default_update_handler)
```

