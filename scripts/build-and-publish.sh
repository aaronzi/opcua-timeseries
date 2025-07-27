#!/bin/bash

# Build and publish script for Docker Hub
# Usage: ./build-and-publish.sh [version]

set -e

# Configuration
DOCKER_USERNAME="aaronzi"
IMAGE_NAME="opcua-timeseries"
VERSION=${1:-"1.0.0"}

echo "🐳 Building and publishing ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build the image
echo "📦 Building Docker image..."
docker build -t "${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}" .

# Tag as latest if this is not a pre-release
if [[ ! "$VERSION" =~ -(alpha|beta|rc) ]]; then
    echo "🏷️  Tagging as latest..."
    docker tag "${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}" "${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
fi

# Login to Docker Hub (if not already logged in)
echo "🔐 Checking Docker Hub authentication..."
if ! docker info | grep -q "Username"; then
    echo "Please login to Docker Hub:"
    docker login
fi

# Push the image
echo "🚀 Pushing to Docker Hub..."
docker push "${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"

if [[ ! "$VERSION" =~ -(alpha|beta|rc) ]]; then
    docker push "${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
fi

echo "✅ Successfully published ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"
echo ""
echo "📋 Usage examples:"
echo "   docker run -p 4840:4840 ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"
echo "   docker pull ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"
echo ""
echo "🔗 Docker Hub: https://hub.docker.com/r/${DOCKER_USERNAME}/${IMAGE_NAME}"
