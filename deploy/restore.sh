#!/usr/bin/env bash
# Restore the database from a dump file.   bash deploy/restore.sh /data/backups/suremedra_XXXX.dump
# WARNING: this REPLACES the current database.
set -euo pipefail
cd "$(dirname "$0")/.."
COMPOSE="docker compose --env-file .env.prod -f docker-compose.prod.yml"
FILE="${1:?Usage: restore.sh <dump-file>}"
[ -f "$FILE" ] || { echo "File not found: $FILE"; exit 1; }

envval() { grep -E "^$1=" .env.example.prod | head -n1 | cut -d= -f2-; }
PG_USER=$(envval POSTGRES_USER); PG_DB=$(envval POSTGRES_DB)

read -r -p "This will ERASE the current '$PG_DB' database and load $FILE. Type YES to continue: " ANSWER
[ "$ANSWER" = "YES" ] || { echo "Cancelled."; exit 1; }

echo "==> Stopping app containers"
$COMPOSE stop web api worker
$COMPOSE up -d db
sleep 5

echo "==> Recreating the database"
$COMPOSE exec -T db psql -U "$PG_USER" -d postgres -c "DROP DATABASE IF EXISTS \"$PG_DB\";"
$COMPOSE exec -T db psql -U "$PG_USER" -d postgres -c "CREATE DATABASE \"$PG_DB\" OWNER \"$PG_USER\";"

echo "==> Loading the dump"
$COMPOSE exec -T db pg_restore -U "$PG_USER" -d "$PG_DB" --no-owner < "$FILE"

echo "==> Starting the app again"
$COMPOSE up -d
echo "Restore finished."
