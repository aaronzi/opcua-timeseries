#!/bin/bash
# Enhanced Docker build script with attestation support

set -e

# Configuration
IMAGE_NAME="aaronzi/opcua-timeseries"
TAG="${1:-latest}"
PLATFORMS="${2:-linux/amd64,linux/arm64}"

echo "🚀 Building OPC UA Time Series Server with attestations..."
echo "📦 Image: ${IMAGE_NAME}:${TAG}"
echo "🏗️  Platforms: ${PLATFORMS}"

# Enable BuildKit
export DOCKER_BUILDKIT=1

# Check if buildx is available
if ! docker buildx version > /dev/null 2>&1; then
    echo "❌ Docker Buildx is required for multi-platform builds and attestations"
    echo "💡 Please update Docker to a newer version or install buildx plugin"
    exit 1
fi

# Create builder if it doesn't exist
if ! docker buildx inspect opcua-builder > /dev/null 2>&1; then
    echo "🔧 Creating new buildx builder..."
    docker buildx create --name opcua-builder --use
fi

# Build with attestations
echo "🔨 Building with SBOM and provenance attestations..."
docker buildx build \
    --builder opcua-builder \
    --platform "${PLATFORMS}" \
    --provenance=mode=max \
    --sbom=true \
    --tag "${IMAGE_NAME}:${TAG}" \
    --load \
    .

echo "✅ Build completed successfully!"
echo "📋 Image: ${IMAGE_NAME}:${TAG}"
echo ""
echo "🔍 To verify attestations (requires docker-scout or cosign):"
echo "   docker scout attestations ${IMAGE_NAME}:${TAG}"
echo ""
echo "🚀 To run the container:"
echo "   docker run -p 4840:4840 ${IMAGE_NAME}:${TAG}"
