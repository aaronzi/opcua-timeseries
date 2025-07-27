@echo off
REM Enhanced Docker build script with attestation support for Windows

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=aaronzi/opcua-timeseries
set TAG=%1
if "%TAG%"=="" set TAG=latest
set PLATFORMS=%2
if "%PLATFORMS%"=="" set PLATFORMS=linux/amd64,linux/arm64

echo 🚀 Building OPC UA Time Series Server with attestations...
echo 📦 Image: %IMAGE_NAME%:%TAG%
echo 🏗️  Platforms: %PLATFORMS%

REM Enable BuildKit
set DOCKER_BUILDKIT=1

REM Check if buildx is available
docker buildx version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Buildx is required for multi-platform builds and attestations
    echo 💡 Please update Docker to a newer version or install buildx plugin
    exit /b 1
)

REM Create builder if it doesn't exist
docker buildx inspect opcua-builder >nul 2>&1
if errorlevel 1 (
    echo 🔧 Creating new buildx builder...
    docker buildx create --name opcua-builder --use
)

REM Build with attestations
echo 🔨 Building with SBOM and provenance attestations...
docker buildx build ^
    --builder opcua-builder ^
    --platform "%PLATFORMS%" ^
    --provenance=mode=max ^
    --sbom=true ^
    --tag "%IMAGE_NAME%:%TAG%" ^
    --load ^
    .

if errorlevel 1 (
    echo ❌ Build failed!
    exit /b 1
)

echo ✅ Build completed successfully!
echo 📋 Image: %IMAGE_NAME%:%TAG%
echo.
echo 🔍 To verify attestations (requires docker-scout or cosign):
echo    docker scout attestations %IMAGE_NAME%:%TAG%
echo.
echo 🚀 To run the container:
echo    docker run -p 4840:4840 %IMAGE_NAME%:%TAG%
