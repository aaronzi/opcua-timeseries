# Supply Chain Security Improvements

This document outlines the security improvements made to address supply chain attestation requirements.

## Overview

The following changes have been implemented to improve supply chain security and provide attestations:

### 1. GitHub Actions Workflow with Attestations

- **File**: `.github/workflows/docker-build-push.yml`
- **Features**:
  - Automated Docker image building with multi-platform support (linux/amd64, linux/arm64)
  - SBOM (Software Bill of Materials) generation using SPDX format
  - Provenance attestations for build transparency
  - Signature verification capabilities
  - Caching for faster builds

### 2. Enhanced Dockerfile Security

- **Pinned system dependencies** with specific versions
- **Enhanced OCI labels** for better metadata
- **Security-first approach** with non-root user
- **Hash verification** support for Python packages
- **Read-only filesystem** support

### 3. Requirements Management

- **Scripts** for generating hashed requirements files
- **Fallback mechanism** in Dockerfile for hash verification
- **Support for pip-tools** for dependency management

### 4. Docker Compose Enhancement

- **Security options** including no-new-privileges
- **Read-only filesystem** with appropriate tmpfs mounts
- **Network isolation** with custom bridge network
- **Health checks** for service monitoring

## Usage

### Building with Attestations (Local)

```bash
# Enable BuildKit for attestation support
export DOCKER_BUILDKIT=1

# Build with SBOM and provenance
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --provenance=mode=max \
  --sbom=true \
  --tag aaronzi/opcua-timeseries:latest \
  .
```

### Automated CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **Builds** multi-platform images
2. **Generates** SBOM in SPDX format
3. **Creates** provenance attestations
4. **Pushes** to Docker Hub with attestations
5. **Uploads** SBOM as build artifact

### Verifying Attestations

After the image is pushed with attestations, you can verify them:

```bash
# Install docker-scout or cosign for verification
docker scout attestations aaronzi/opcua-timeseries:latest

# Or using cosign
cosign verify-attestation \
  --type slsaprovenance \
  aaronzi/opcua-timeseries:latest
```

## Security Benefits

1. **Supply Chain Transparency**: SBOM provides complete inventory of components
2. **Build Provenance**: Verifiable record of how the image was built
3. **Integrity Verification**: Cryptographic signatures ensure image hasn't been tampered with
4. **Compliance**: Meets industry standards for software supply chain security
5. **Vulnerability Tracking**: SBOM enables better vulnerability management

## Prerequisites

### For CI/CD Pipeline

Add these secrets to your GitHub repository:

- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password or access token

### For Local Development

- Docker Buildx enabled
- Optional: pip-tools for hashed requirements generation

## Migration Guide

1. **Update your CI/CD**: Use the provided GitHub Actions workflow
2. **Configure secrets**: Add Docker Hub credentials to GitHub secrets
3. **Test locally**: Use the enhanced docker-compose.yml for local development
4. **Verify attestations**: Use docker-scout or cosign to verify pushed images

## Compliance Standards

This implementation helps meet:

- **SLSA Level 2+**: Build provenance and integrity
- **NIST SSDF**: Secure software development framework
- **Executive Order 14028**: Software supply chain security requirements
- **CISA guidance**: Software bill of materials requirements
