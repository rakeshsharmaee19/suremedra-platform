#!/usr/bin/env bash
# Update the running site to the latest code:   bash deploy/deploy.sh
set -euo pipefail
cd "$(dirname "$0")/.."
COMPOSE="docker compose --env-file .env.prod -f docker-compose.prod.yml"

echo "==> Backing up the database before deploying"
if $COMPOSE ps --status running db 2>/dev/null | grep -q db; then
  bash deploy/backup.sh || { echo "Backup failed; aborting deploy."; exit 1; }
fi

echo "==> Pulling latest code"
git pull --ff-only

echo "==> Building images (this takes a few minutes the first time)"
$COMPOSE build

echo "==> Starting database and cache"
$COMPOSE up -d db redis

echo "==> Applying database migrations"
$COMPOSE run --rm api python manage.py migrate --noinput

echo "==> Starting everything"
$COMPOSE up -d --remove-orphans

echo "==> Cleaning old images"
docker image prune -f >/dev/null

echo "==> Status"
$COMPOSE ps
echo "Deploy finished at $(date)"
