#!/usr/bin/env bash
# Minimal staging deploy — run ON the staging host (or via `ssh staging bash -s` < this file).
# Assumes: Docker + Docker Compose v2 already installed, repo already cloned once,
# and a real `.env` + `backend/.env` already in place (never committed, copied by hand
# or by your secrets manager on first setup).
#
# Usage: ./scripts/deploy-staging.sh [git-ref]   (default: origin/main)

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

REF="${1:-origin/main}"

echo "==> Fetching and checking out ${REF}"
git fetch origin
git checkout "${REF}"

echo "==> Building images"
docker compose -f compose.yaml build

echo "==> Starting stack (zero-downtime for db/redis, brief blip for php/nginx)"
docker compose -f compose.yaml up -d

echo "==> Waiting for php container to be ready"
for i in $(seq 1 30); do
  if docker compose -f compose.yaml exec -T php php artisan about >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo "==> Running migrations"
docker compose -f compose.yaml exec -T php php artisan migrate --force

echo "==> Clearing/rebuilding config + route cache"
docker compose -f compose.yaml exec -T php php artisan config:clear
docker compose -f compose.yaml exec -T php php artisan config:cache
docker compose -f compose.yaml exec -T php php artisan route:cache

echo "==> Healthcheck (via nginx container — no host port is published for it directly)"
docker compose -f compose.yaml exec -T nginx wget --spider -q http://localhost/up && echo "OK: /up healthy" || {
  echo "FAILED: /up is not healthy after deploy — check 'docker compose logs php'";
  exit 1;
}

echo "==> Done. Deployed ${REF}."
