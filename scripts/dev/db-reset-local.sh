#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [[ ! -f apps/api/.env ]]; then
  cp apps/api/.env.example apps/api/.env
fi

docker compose up -d postgres
for _ in $(seq 1 30); do
  if docker compose exec -T postgres pg_isready -U japan -d postgres >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

docker compose exec -T postgres psql -U japan -d postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'japan_travel' AND pid <> pg_backend_pid();"
docker compose exec -T postgres psql -U japan -d postgres -c "DROP DATABASE IF EXISTS japan_travel;"
docker compose exec -T postgres psql -U japan -d postgres -c "CREATE DATABASE japan_travel;"

pnpm --filter @japan-travel/api migrate
pnpm --filter @japan-travel/api seed
