#!/bin/bash
# Script to verify Docker image attestations

set -e

IMAGE="${1:-aaronzi/opcua-timeseries:latest}"

echo "🔍 Verifying attestations for image: ${IMAGE}"
echo ""

# Check if docker scout is available
if command -v docker-scout > /dev/null 2>&1 || docker scout version > /dev/null 2>&1; then
    echo "📋 Checking SBOM with Docker Scout..."
    docker scout attestations "${IMAGE}" || echo "⚠️  No attestations found or Docker Scout not configured"
    echo ""
    
    echo "🛡️  Checking vulnerabilities with Docker Scout..."
    docker scout cves "${IMAGE}" || echo "⚠️  Could not scan for vulnerabilities"
    echo ""
else
    echo "⚠️  Docker Scout not available. Install with: docker scout version"
fi

# Check if cosign is available
if command -v cosign > /dev/null 2>&1; then
    echo "🔐 Verifying signatures with Cosign..."
    cosign verify-attestation --type slsaprovenance "${IMAGE}" || echo "⚠️  No cosign attestations found"
    echo ""
else
    echo "⚠️  Cosign not available. Install from: https://github.com/sigstore/cosign"
fi

# Check if crane is available for manifest inspection
if command -v crane > /dev/null 2>&1; then
    echo "📦 Inspecting image manifest..."
    crane manifest "${IMAGE}" | jq '.mediaType, .schemaVersion' || echo "⚠️  Could not inspect manifest"
    echo ""
else
    echo "⚠️  Crane not available. Install from: https://github.com/google/go-containerregistry"
fi

# Basic Docker inspection
echo "🏷️  Image labels and metadata..."
docker inspect "${IMAGE}" --format='{{json .Config.Labels}}' | jq . || echo "⚠️  Could not inspect image"

echo ""
echo "✅ Verification complete!"
echo ""
echo "📚 For more information:"
echo "   - Docker Scout: https://docs.docker.com/scout/"
echo "   - Cosign: https://docs.sigstore.dev/cosign/overview/"
echo "   - SLSA: https://slsa.dev/"
