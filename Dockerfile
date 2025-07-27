FROM python:3.13-slim

# Metadata labels for Docker Hub
LABEL maintainer="aaronzi"
LABEL description="OPC UA Time Series Server"
LABEL version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/aaronzi/opcua-timeseries"
LABEL org.opencontainers.image.description="A containerized OPC UA server for time series data"
LABEL org.opencontainers.image.licenses="MIT"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ ./server/
COPY config/ ./config/

# Create logs directory
RUN mkdir -p logs

# Expose OPC UA port
EXPOSE 4840

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN groupadd -r opcua && useradd -r -g opcua opcua
RUN chown -R opcua:opcua /app
USER opcua

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import asyncio; from server.client_test import test_connection; asyncio.run(test_connection())" || exit 1

# Run the server
CMD ["python", "-m", "server.main"]
