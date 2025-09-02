#!/usr/bin/env bash
set -euo pipefail
:
# Usage: restore.sh <mode> [options]
# Modes:
#   full <file>                - restore full DB from custom-format dump (pg_restore)
#   tenant <tenant_id> <file>  - restore a single tenant schema from custom-format dump
#   sqlfile <file>             - apply a plain SQL file (e.g., global dump)
# Environment variables used:
#   DATABASE_URL       - postgres connection string (required)

if ! command -v pg_restore >/dev/null 2>&1; then
  echo "pg_restore is required but not found in PATH" >&2
  exit 2
fi

if [ -z "${DATABASE_URL:-}" ]; then
  echo "Please set DATABASE_URL environment variable (postgres connection string)" >&2
  exit 2
fi

MODE=${1:-}
shift || true

case "$MODE" in
  full)
    FILE=${1:-}
    if [ -z "$FILE" ]; then
      echo "Usage: $0 full <dumpfile.dump|dumpfile.dump.gz>" >&2
      exit 2
    fi
    if [[ "$FILE" == *.gz ]]; then
      echo "Decompressing $FILE"
      gunzip -c "$FILE" > /tmp/restore_full.dump
      FILE=/tmp/restore_full.dump
    fi
    echo "Restoring full DB from $FILE (this will overwrite existing objects)"
    pg_restore --verbose --clean --no-owner --dbname="$DATABASE_URL" "$FILE"
    ;;

  tenant)
    TENANT_ID=${1:-}
    FILE=${2:-}
    if [ -z "$TENANT_ID" ] || [ -z "$FILE" ]; then
      echo "Usage: $0 tenant <tenant_id> <dumpfile.dump|dumpfile.dump.gz>" >&2
      exit 2
    fi
    schema="tenant_${TENANT_ID}"
    if [[ "$FILE" == *.gz ]]; then
      echo "Decompressing $FILE"
      gunzip -c "$FILE" > /tmp/restore_tenant.dump
      FILE=/tmp/restore_tenant.dump
    fi
    echo "Restoring schema $schema from $FILE"
    # Drop schema if exists, then restore schema-only from dump
    psql "$DATABASE_URL" -c "DROP SCHEMA IF EXISTS \"$schema\" CASCADE; CREATE SCHEMA \"$schema\";"
    pg_restore --verbose --schema="$schema" --no-owner --dbname="$DATABASE_URL" "$FILE"
    ;;

  sqlfile)
    FILE=${1:-}
    if [ -z "$FILE" ]; then
      echo "Usage: $0 sqlfile <file.sql.gz|file.sql>" >&2
      exit 2
    fi
    if [[ "$FILE" == *.gz ]]; then
      gunzip -c "$FILE" | psql "$DATABASE_URL"
    else
      psql "$DATABASE_URL" -f "$FILE"
    fi
    ;;

  *)
    echo "Unknown mode: $MODE" >&2
    exit 2
    ;;
esac

echo "Done"
