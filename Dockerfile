FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variable placeholders
ENV SMARTAPI_API_KEY=""
ENV SMARTAPI_CLIENT_CODE=""
ENV SMARTAPI_PASSWORD=""
ENV SMARTAPI_TOTP=""
ENV GCS_BUCKET=""
ENV GOOGLE_APPLICATION_CREDENTIALS=""
ENV REDIS_HOST="localhost"
ENV REDIS_PORT="6379"
ENV REDIS_DB="0"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
