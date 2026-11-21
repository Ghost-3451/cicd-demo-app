#!/usr/bin/env bash
set -euo pipefail
port="${1:?Usage: bash scripts/verify.sh PORT}"
response="$(curl --fail --silent --show-error --noproxy '*' \
    --connect-timeout 3 --max-time 10 "http://127.0.0.1:${port}/health")"
printf '%s\n' "$response"
printf '%s' "$response" | python3 -c \
    'import json,sys; body=json.load(sys.stdin); sys.exit(0 if body=={"status":"ok"} else "Unexpected /health response")'
