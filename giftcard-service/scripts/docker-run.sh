#!/usr/bin/env bash
set -euo pipefail

IMAGE=${IMAGE:-giftcard-service:latest}
NOTIFICATION_QUEUE_URL=${NOTIFICATION_QUEUE_URL:-}
FISERV_URL=${FISERV_URL:-}

# Build image
docker build -t "$IMAGE" .

# Run container
docker run --rm -p 8000:8000 \
  -e NOTIFICATION_QUEUE_URL="$NOTIFICATION_QUEUE_URL" \
  -e FISERV_URL="$FISERV_URL" \
  "$IMAGE"
