FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Set environment variables
ENV PYTHONPATH=/workspace
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/opcua/.local/bin:${PATH}"
