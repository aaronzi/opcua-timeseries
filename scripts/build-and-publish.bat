@echo off
REM Build and publish script for Docker Hub (Windows)
REM Usage: build-and-publish.bat [version]

setlocal

REM Configuration
set DOCKER_USERNAME=aaronzi
set IMAGE_NAME=opcua-timeseries
if "%1"=="" (
    set VERSION=1.0.0
) else (
    set VERSION=%1
)

echo 🐳 Building and publishing %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Build the image
echo 📦 Building Docker image...
docker build -t %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% .
if errorlevel 1 exit /b 1

REM Tag as latest if this is not a pre-release
echo %VERSION% | findstr /R "alpha\|beta\|rc" >nul
if errorlevel 1 (
    echo 🏷️  Tagging as latest...
    docker tag %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% %DOCKER_USERNAME%/%IMAGE_NAME%:latest
)

REM Check Docker Hub authentication
echo 🔐 Checking Docker Hub authentication...
docker info | findstr "Username" >nul
if errorlevel 1 (
    echo Please login to Docker Hub:
    docker login
    if errorlevel 1 exit /b 1
)

REM Push the image
echo 🚀 Pushing to Docker Hub...
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
if errorlevel 1 exit /b 1

echo %VERSION% | findstr /R "alpha\|beta\|rc" >nul
if errorlevel 1 (
    docker push %DOCKER_USERNAME%/%IMAGE_NAME%:latest
    if errorlevel 1 exit /b 1
)

echo ✅ Successfully published %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
echo.
echo 📋 Usage examples:
echo    docker run -p 4840:4840 %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
echo    docker pull %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
echo.
echo 🔗 Docker Hub: https://hub.docker.com/r/%DOCKER_USERNAME%/%IMAGE_NAME%

endlocal
