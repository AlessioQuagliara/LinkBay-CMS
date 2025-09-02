#!/usr/bin/env bash
set -euo pipefail
:
# Usage: backup.sh [mode] [options]
# Modes:
#   full               - full DB dump (recommended for full restore)
#   global             - dump only global tables (non-tenant schema)
#   tenants-schemas    - dump each tenant schema separately and upload as per-tenant files
#   tenant <id>        - dump single tenant schema tenant_<id>
# Environment variables used:
#   DATABASE_URL       - postgres connection string (required)
#   S3_BUCKET          - optional, if set will upload backups to s3://$S3_BUCKET/
#   S3_PATH            - optional prefix inside bucket
#   AWS_PROFILE/AWS_REGION - optional for aws cli

if ! command -v pg_dump >/dev/null 2>&1; then
  echo "pg_dump is required but not found in PATH" >&2
  exit 2
fi

if ! command -v gzip >/dev/null 2>&1; then
  echo "gzip is required but not found in PATH" >&2
  exit 2
fi

MODE=${1:-full}
shift || true
TS=$(date -u +%Y%m%dT%H%M%SZ)
OUTDIR=${OUTDIR:-./backups}
mkdir -p "$OUTDIR"

if [ -z "${DATABASE_URL:-}" ]; then
  echo "Please set DATABASE_URL environment variable (postgres connection string)" >&2
  exit 2
fi

upload_to_s3() {
  local file=$1
  if [ -n "${S3_BUCKET:-}" ]; then
    local prefix=${S3_PATH:-backups}
    local dest="s3://${S3_BUCKET}/${prefix}/$(basename "$file")"
    echo "Uploading $file => $dest"
    aws s3 cp "$file" "$dest"
    echo "$dest"
  else
    echo "$file"
  fi
}

case "$MODE" in
  full)
    FILE="$OUTDIR/linkbay_full_${TS}.dump"
    echo "Creating full DB dump to $FILE"
    pg_dump --format=custom --file="$FILE" "$DATABASE_URL"
    gzip -f "$FILE"
    upload_to_s3 "$FILE.gz"
    ;;

  global)
    FILE="$OUTDIR/linkbay_global_${TS}.sql.gz"
    echo "Dumping global public tables (excluding tenant schemas)"
    # Dump everything but tenant schemas (assumes tenant schemas are named tenant_<id>)
    pg_dump --format=plain --file=- "$DATABASE_URL" --exclude-schema='tenant_*' | gzip -c > "$FILE"
    upload_to_s3 "$FILE"
    ;;

  tenants-schemas)
    echo "Dumping each tenant schema separately"
    # retrieve tenant ids from DB
    TENANTS=$(psql "$DATABASE_URL" -t -A -c "SELECT id FROM tenants;" )
    for id in $TENANTS; do
      schema="tenant_${id}"
      FILE="$OUTDIR/${schema}_${TS}.dump"
      echo "Dumping schema $schema -> $FILE"
      pg_dump --format=custom --file="$FILE" --schema="$schema" "$DATABASE_URL"
      gzip -f "$FILE"
      upload_to_s3 "$FILE.gz"
    done
    ;;

  tenant)
    TENANT_ID=${1:-}
    if [ -z "$TENANT_ID" ]; then
      echo "Usage: $0 tenant <id>" >&2
      exit 2
    fi
    schema="tenant_${TENANT_ID}"
    FILE="$OUTDIR/${schema}_${TS}.dump"
    echo "Dumping schema $schema -> $FILE"
    pg_dump --format=custom --file="$FILE" --schema="$schema" "$DATABASE_URL"
    gzip -f "$FILE"
    upload_to_s3 "$FILE.gz"
    ;;

  *)
    echo "Unknown mode: $MODE" >&2
    exit 2
    ;;
esac

echo "Done"
