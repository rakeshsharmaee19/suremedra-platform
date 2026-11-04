#!/bin/sh

set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Seeding demo data..."
python manage.py seed_demo

echo "Starting Gunicorn..."

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers 1 \
    --threads 4 \
    --timeout 120 \
    --log-level info \
    --error-logfile -