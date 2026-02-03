#!/usr/bin/env bash
set -euo pipefail

ORDER_ID=${1:-ORD-FT-001}

echo "Creating Order ${ORDER_ID}"
curl -s -X POST http://localhost:8080/orders \
  -H "Content-Type: application/json" \
  -d '{"orderId":"'${ORDER_ID}'","customerId":"CUST-1","amount":10.0,"timestamp":"2026-01-01T00:00:00Z"}'

echo "Waiting for fulfillment..."
for i in {1..20}; do
  sleep 2
  resp=$(curl -s http://localhost:8080/orders/${ORDER_ID} || true)
  if [[ "$resp" == "" ]]; then
    echo "Order not found yet..."
    continue
  fi
  echo "Order: $resp"
  echo "$resp" | grep -q 'FULFILLED' && break
done

echo "Done."
