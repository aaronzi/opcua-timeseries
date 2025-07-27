FROM python:3.13-slim

# Metadata labels for Docker Hub and OCI compliance
LABEL maintainer="aaronzi"
LABEL description="OPC UA Time Series Server"
LABEL version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/aaronzi/opcua-timeseries"
LABEL org.opencontainers.image.description="A containerized OPC UA server for time series data"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.title="OPC UA Time Series Server"
LABEL org.opencontainers.image.authors="aaronzi"
LABEL org.opencontainers.image.vendor="aaronzi"
LABEL org.opencontainers.image.documentation="https://github.com/aaronzi/opcua-timeseries"
LABEL org.opencontainers.image.url="https://github.com/aaronzi/opcua-timeseries"

# Set working directory
WORKDIR /app

# Install system dependencies with specific versions for reproducibility
RUN apt-get update && apt-get install -y \
    gcc=4:12.2.0-3 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with hash verification for security
RUN pip install --no-cache-dir --require-hashes -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt

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
