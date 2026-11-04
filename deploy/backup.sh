#!/usr/bin/env bash
# Dump the database and copy it to S3.  Run by cron every hour (see docs/OPERATIONS.md).
set -euo pipefail
cd "$(dirname "$0")/.."
COMPOSE="docker compose --env-file .env.prod -f docker-compose.prod.yml"

envval() { grep -E "^$1=" .env.example.prod | head -n1 | cut -d= -f2-; }
PG_USER=$(envval POSTGRES_USER); PG_DB=$(envval POSTGRES_DB); BUCKET=$(envval BACKUP_S3_BUCKET)

BACKUP_DIR=/data/backups
mkdir -p "$BACKUP_DIR"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
FILE="$BACKUP_DIR/suremedra_${STAMP}.dump"

$COMPOSE exec -T db pg_dump -U "$PG_USER" -Fc "$PG_DB" > "$FILE"
if [ ! -s "$FILE" ]; then
  echo "$(date -u) BACKUP FAILED: empty dump" >> "$BACKUP_DIR/backup.log"
  rm -f "$FILE"; exit 1
fi

aws s3 cp "$FILE" "s3://${BUCKET}/backups/$(date -u +%Y/%m/%d)/$(basename "$FILE")" --only-show-errors
find "$BACKUP_DIR" -name '*.dump' -mtime +2 -delete    # keep 2 days locally; S3 keeps the rest
echo "$(date -u) backup ok: $(basename "$FILE") ($(du -h "$FILE" | cut -f1))" >> "$BACKUP_DIR/backup.log"
