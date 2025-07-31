# TradingBot SmartAPI v2.0

A modern, production-ready trading bot that integrates with Angel One's SmartAPI for automated trading based on TradingView webhooks. Built with FastAPI, async/await patterns, and comprehensive error handling.

## 🚀 Features

- **Modern Architecture**: Built with FastAPI, Pydantic v2, and async/await patterns
- **Robust Error Handling**: Comprehensive exception handling with retry logic
- **Real-time Updates**: WebSocket integration for live order updates
- **Position Tracking**: Redis-based position management with persistence
- **Token Management**: Automatic token refresh with Google Cloud Storage backup
- **Monitoring**: Prometheus metrics and structured logging
- **Production Ready**: Docker support, health checks, and graceful shutdown
- **Type Safety**: Full type hints and Pydantic validation
- **Testing**: Comprehensive test suite with pytest

## 📋 Requirements

- Python 3.9+
- Redis server
- Google Cloud Storage (optional, for token persistence)
- Angel One SmartAPI credentials

## 🛠️ Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repo-url>
cd tradingbot-smartapi
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Configure your credentials in `.env`

4. Start with Docker Compose:
```bash
docker-compose up -d
```

### Manual Installation

1. Install dependencies:
```bash
pip install -e .
```

2. Configure environment variables in `.env`

3. Start Redis server

4. Run the application:
```bash
python -m tradingbot.main
```

## 🔧 Configuration

All configuration is handled through environment variables. See `.env.example` for all available options.

### Required Variables

- `SMARTAPI_API_KEY`: Your SmartAPI API key
- `SMARTAPI_CLIENT_CODE`: Your SmartAPI client code  
- `SMARTAPI_PASSWORD`: Your SmartAPI password
- `SMARTAPI_TOTP`: Your TOTP secret for 2FA

### Optional Variables

- `GCS_BUCKET`: Google Cloud Storage bucket for token persistence
- `REDIS_HOST`: Redis server host (default: localhost)
- `DEBUG`: Enable debug mode (default: false)

## 📡 API Endpoints

### Health Checks
- `GET /health/` - Basic health check
- `GET /health/ready` - Readiness check with dependencies

### Authentication
- `POST /auth/login` - Authenticate with SmartAPI
- `POST /auth/logout` - Logout and cleanup
- `GET /auth/status` - Get authentication status

### Webhooks
- `POST /webhook/tradingview` - Process TradingView webhooks
- `GET /webhook/test` - Test webhook endpoint

### Positions
- `GET /positions/` - Get all positions
- `GET /positions/{symbol}` - Get position for symbol
- `DELETE /positions/{symbol}` - Clear position for symbol
- `DELETE /positions/` - Clear all positions

### Monitoring
- `GET /metrics` - Prometheus metrics

## 📊 TradingView Integration

Send JSON payloads to `/webhook/tradingview`:

### Market Order Example
```json
{
  "symbol": "SBIN-EQ",
  "side": "BUY",
  "qty": 10,
  "order_type": "MARKET",
  "product_type": "INTRADAY",
  "exchange": "NSE"
}
```

### Limit Order Example
```json
{
  "symbol": "SBIN-EQ",
  "side": "SELL", 
  "qty": 10,
  "price": 205.5,
  "order_type": "LIMIT",
  "product_type": "DELIVERY",
  "exchange": "NSE"
}
```

## 🏗️ Architecture

```
tradingbot/
├── core/                 # Core configuration and utilities
│   ├── config.py        # Pydantic settings
│   ├── exceptions.py    # Custom exceptions
│   └── logging.py       # Structured logging
├── models/              # Pydantic models
│   └── orders.py        # Order and position models
├── services/            # Business logic services
│   ├── smartapi_client.py    # Enhanced SmartAPI client
│   ├── token_manager.py      # Token persistence
│   └── position_manager.py   # Position tracking
├── api/                 # FastAPI application
│   ├── dependencies.py  # FastAPI dependencies
│   ├── middleware.py    # Custom middleware
│   └── routes/          # API route handlers
└── main.py             # Application entry point
```

## 🧪 Testing

Run the test suite:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest --cov=tradingbot --cov-report=html

# Run specific test file
pytest tests/test_smartapi_client.py -v
```

## 📈 Monitoring

The application includes:

- **Structured Logging**: JSON logs with request tracing
- **Prometheus Metrics**: Available at `/metrics`
- **Health Checks**: Kubernetes-ready health endpoints
- **Request Tracing**: Unique request IDs for debugging

## 🚀 Deployment

### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/tradingbot
gcloud run deploy tradingbot \
  --image gcr.io/PROJECT_ID/tradingbot \
  --platform managed \
  --region us-central1 \
  --set-env-vars SMARTAPI_API_KEY=xxx,...
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tradingbot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tradingbot
  template:
    metadata:
      labels:
        app: tradingbot
    spec:
      containers:
      - name: tradingbot
        image: your-registry/tradingbot:latest
        ports:
        - containerPort: 8080
        env:
        - name: SMARTAPI_API_KEY
          valueFrom:
            secretKeyRef:
              name: tradingbot-secrets
              key: api-key
        livenessProbe:
          httpGet:
            path: /health/
            port: 8080
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
```

## 🔒 Security

- Non-root Docker container
- Environment variable configuration
- Input validation with Pydantic
- Structured error responses
- Request rate limiting (configurable)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the logs for detailed error messages
2. Verify your SmartAPI credentials
3. Ensure Redis is running and accessible
4. Check the health endpoints for system status

## 🔄 Migration from v1.0

The new version includes breaking changes:

1. **Configuration**: Now uses Pydantic settings instead of environment variables directly
2. **API**: New endpoint structure with proper REST conventions  
3. **Models**: Pydantic v2 models with validation
4. **Async**: Full async/await support throughout
5. **Error Handling**: Structured exceptions with error codes

See the migration guide for detailed upgrade instructions.