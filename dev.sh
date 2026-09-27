#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ ! -f apps/api/.env ]]; then
  cp apps/api/.env.example apps/api/.env
fi

docker compose up -d postgres redis minio mailhog

echo "Waiting for Postgres..."
for _ in $(seq 1 30); do
  if docker compose exec -T postgres pg_isready -U japan -d japan_travel >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

pnpm --filter @japan-travel/api migrate
pnpm --filter @japan-travel/api seed

pnpm run dev:api &
API_PID=$!
pnpm run dev:worker &
WORKER_PID=$!
pnpm run dev:web &
WEB_PID=$!

trap 'kill $API_PID $WORKER_PID $WEB_PID 2>/dev/null || true' EXIT INT TERM
wait
