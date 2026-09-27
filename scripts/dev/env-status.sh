#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ENV_FILE="$ROOT/apps/api/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "No apps/api/.env — copy apps/api/.env.example"
  exit 1
fi

echo "Environment file: apps/api/.env"
grep -E '^(DATABASE_URL|REDIS_URL|ENVIRONMENT|CORS_ORIGINS)=' "$ENV_FILE" || true
