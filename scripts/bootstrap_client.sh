#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------------------
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SPEC_URL="https://kunde.comdirect.de/cms/media/comdirect_rest_api_swagger.json"
SPEC_FILE="$ROOT/tmp/comdirect_openapi.json"

GEN_DIR="$ROOT/tmp/generated_client"
DEST_DIR="$ROOT/src/openapi_client"

# ------------------------------------------------------------------------------
# Prerequisites
# ------------------------------------------------------------------------------
command -v curl >/dev/null || { echo "curl missing"; exit 1; }
command -v openapi-generator-cli >/dev/null || { echo "openapi-generator-cli missing"; exit 1; }
command -v python >/dev/null || { echo "python missing"; exit 1; }

mkdir -p "$ROOT/tmp"

# ------------------------------------------------------------------------------
# Download OpenAPI spec
# ------------------------------------------------------------------------------
echo "Downloading OpenAPI spec ..."
curl -fsSL -o "$SPEC_FILE" "$SPEC_URL"

# ------------------------------------------------------------------------------
# Patch broken schemas
# ------------------------------------------------------------------------------
echo "Patching OpenAPI spec ..."
python "$ROOT/scripts/patch_openapi.py"

# ------------------------------------------------------------------------------
# Generate Python client
# ------------------------------------------------------------------------------
echo "Generating Python client ..."
rm -rf "$GEN_DIR"

openapi-generator-cli generate \
  -i "$SPEC_FILE" \
  -g python \
  -o "$GEN_DIR" \
  --package-name openapi_client \
  --global-property modelTests=false,apiTests=false \
  --skip-validate-spec

# ------------------------------------------------------------------------------
# Integrate into source tree
# ------------------------------------------------------------------------------
echo "Integrating generated client ..."
rm -rf "$DEST_DIR"
mkdir -p "$(dirname "$DEST_DIR")"
cp -r "$GEN_DIR/openapi_client" "$DEST_DIR"

# ------------------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------------------
rm -rf "$GEN_DIR"
rm -f "$SPEC_FILE"

echo "✔ Client successfully updated at:"
echo "  $DEST_DIR"
