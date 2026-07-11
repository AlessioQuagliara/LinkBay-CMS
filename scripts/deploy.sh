#!/usr/bin/env bash
# deploy.sh — rsync-based production deploy for LinkBay-CMS.
#
# Run from your Mac. Ships CODE ONLY to the server via rsync, then builds and
# restarts the Docker stack remotely over SSH. Never syncs any secret: every
# .env/.env.* file anywhere in the tree is excluded (see EXCLUDES below) — the
# server's backend/.env and frontend/.env.production.local must already exist,
# created by hand once (or by your secrets manager), and this script refuses
# to proceed if either is missing rather than deploying into a broken app.
#
# Usage:
#   SERVER_HOST=alessio@203.0.113.10 REMOTE_DIR=/var/www/LinkBay-CMS ./scripts/deploy.sh
#
# Optional env vars:
#   SSH_PORT       default 22
#   COMPOSE_FILES  default "-f compose.yaml -f compose.prod.yaml"
#                  (use "-f compose.yaml" only if you haven't set up TLS yet —
#                  see compose.prod.yaml's header for what that needs first)
#   SKIP_CONFIRM   set to "1" to skip the dry-run confirmation prompt (CI use)

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

SERVER_HOST="${SERVER_HOST:?Set SERVER_HOST, e.g. alessio@203.0.113.10}"
REMOTE_DIR="${REMOTE_DIR:?Set REMOTE_DIR, e.g. /var/www/LinkBay-CMS}"
SSH_PORT="${SSH_PORT:-22}"
COMPOSE_FILES="${COMPOSE_FILES:--f compose.yaml -f compose.prod.yaml}"
SKIP_CONFIRM="${SKIP_CONFIRM:-0}"

SSH_CMD=(ssh -p "${SSH_PORT}")
RSYNC_SSH="ssh -p ${SSH_PORT}"

# ── Never sync secrets — every .env variant, anywhere in the tree ───────────
# rsync has no "!" negation for --exclude; to let .env.example (template, not
# a secret) through past the broader .env* exclusion below, the --include has
# to come FIRST — rsync's filter rules are first-match-wins, in list order.
EXCLUDES=(
  --include='.env.example'
  --include='**/.env.example'
  --exclude='.env'
  --exclude='.env.*'
  --exclude='**/.env'
  --exclude='**/.env.*'

  # Reinstalled/rebuilt on the server, never shipped from a local machine —
  # avoids platform-mismatched native binaries (Mac arm64/Darwin vs a Linux
  # server) and stale local build artifacts overwriting a fresh remote build.
  # Unanchored (no leading path) on purpose: matches vendor/ or node_modules/
  # at ANY depth, including a stray root-level vendor/ this repo happens to
  # have lying around from before backend/ was split out — not just backend/vendor/.
  --exclude='vendor/'
  --exclude='node_modules/'
  --exclude='backend/public/build/'
  --exclude='frontend/.next/'

  # Runtime state — bind-mounted (laravel_storage volume), never overwritten
  # by a deploy: logs, sessions, framework cache, any tenant-uploaded media.
  --exclude='backend/storage/'
  --exclude='backend/bootstrap/cache/*.php'

  # Dev/CI-only, not needed on the server
  --exclude='backend/tests/'
  --exclude='frontend/e2e/'
  --exclude='frontend/test-results/'
  --exclude='frontend/playwright-report/'
  --exclude='.git/'
  --exclude='.github/'
  --exclude='backend/.phpunit.cache'
  --exclude='backend/.phpunit.result.cache'
  --exclude='*.sqlite'
  --exclude='*.log'
  --exclude='.DS_Store'
  --exclude='.idea/'
  --exclude='.vscode/'
)

echo "==> Preflight: checking secrets already exist on the server (never synced by this script)"
if ! "${SSH_CMD[@]}" "${SERVER_HOST}" "test -f '${REMOTE_DIR}/backend/.env'"; then
  echo "FAILED: ${REMOTE_DIR}/backend/.env does not exist on the server."
  echo "Create it by hand first (see backend/.env.example for what it needs) — this script will not create or sync it for you."
  exit 1
fi
if ! "${SSH_CMD[@]}" "${SERVER_HOST}" "test -f '${REMOTE_DIR}/.env'"; then
  echo "FAILED: ${REMOTE_DIR}/.env (root) does not exist on the server."
  echo "Create it by hand first (see .env.example for what it needs)."
  exit 1
fi
if ! "${SSH_CMD[@]}" "${SERVER_HOST}" "test -f '${REMOTE_DIR}/frontend/.env.production.local'"; then
  echo "FAILED: ${REMOTE_DIR}/frontend/.env.production.local does not exist on the server."
  echo "Create it by hand first (see frontend/.env.example) — Next.js bakes NEXT_PUBLIC_* into"
  echo "the build from this file, so it must exist before 'docker compose build' runs."
  exit 1
fi
echo "OK: backend/.env, .env, frontend/.env.production.local all present on the server."

echo "==> Dry-run rsync (review before the real sync — nothing is written yet)"
rsync -avzn --delete "${EXCLUDES[@]}" -e "${RSYNC_SSH}" ./ "${SERVER_HOST}:${REMOTE_DIR}/"

if [[ "${SKIP_CONFIRM}" != "1" ]]; then
  read -r -p "Proceed with the real rsync above? [y/N] " confirm
  if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
    echo "Aborted — nothing was synced."
    exit 1
  fi
fi

echo "==> Rsync (real)"
rsync -avz --delete "${EXCLUDES[@]}" -e "${RSYNC_SSH}" ./ "${SERVER_HOST}:${REMOTE_DIR}/"

echo "==> Remote: build assets, build images, restart stack, migrate, cache, healthcheck"
# Deliberately an UNQUOTED heredoc: ${REMOTE_DIR} and ${COMPOSE_FILES} must
# expand HERE, locally, with their real values baked into the text sent over
# SSH — COMPOSE_FILES contains spaces ("-f compose.yaml -f compose.prod.yaml"),
# and passing multi-word values as `VAR="a b" cmd` on an ssh command line
# doesn't survive: ssh just space-joins all its trailing arguments into one
# string before the remote shell re-parses it, which would split COMPOSE_FILES
# back apart on the far end. Baking the values in as literal text here avoids
# that entirely. Everything meant to run on the REMOTE side instead ($(pwd),
# $i, $(seq ...)) is backslash-escaped so it survives to be evaluated remotely,
# not on this Mac.
"${SSH_CMD[@]}" "${SERVER_HOST}" bash -s <<REMOTE_SCRIPT
set -euo pipefail
cd "${REMOTE_DIR}"

echo "--> Building Vite/Filament assets (ephemeral Node container — the php"
echo "    image has no Node; these files are bind-mounted, so they must exist"
echo "    on THIS host's filesystem, not just inside an image layer)"
docker run --rm -v "\$(pwd)/backend:/app" -w /app node:24-alpine \\
  sh -c "npm ci && npm run build"

echo "--> docker compose build"
docker compose ${COMPOSE_FILES} build

echo "--> docker compose up -d"
docker compose ${COMPOSE_FILES} up -d

echo "--> Waiting for php to be ready"
for i in \$(seq 1 30); do
  if docker compose ${COMPOSE_FILES} exec -T php php artisan about >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo "--> Running migrations"
docker compose ${COMPOSE_FILES} exec -T php php artisan migrate --force

echo "--> Clearing/rebuilding config, route, view, event caches"
docker compose ${COMPOSE_FILES} exec -T php php artisan config:clear
docker compose ${COMPOSE_FILES} exec -T php php artisan config:cache
docker compose ${COMPOSE_FILES} exec -T php php artisan route:cache
docker compose ${COMPOSE_FILES} exec -T php php artisan view:cache
docker compose ${COMPOSE_FILES} exec -T php php artisan event:cache

echo "--> Healthcheck (via nginx container — checks central DB + Redis, not just 'nginx is up')"
docker compose ${COMPOSE_FILES} exec -T nginx wget --spider -q http://127.0.0.1/up && echo "OK: /up healthy" || {
  echo "FAILED: /up is not healthy after deploy — check 'docker compose logs php'"
  exit 1
}
REMOTE_SCRIPT

echo "==> Done."
