#!/usr/bin/env bash
set -euo pipefail

# Export env vars if needed
: "${NOTIFICATION_QUEUE_URL:=}"
: "${FISERV_URL:=}"

# Run the FastAPI app (development)
exec uvicorn app:app --host 0.0.0.0 --port 8000 --reload
