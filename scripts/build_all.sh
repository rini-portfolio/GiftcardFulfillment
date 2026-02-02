#!/usr/bin/env bash
set -euo pipefail

echo "Starting full build and test run..."
# Use make for orchestration
make all

echo "Build and test run finished successfully."