#!/bin/sh

set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Seeding demo data..."
python manage.py import_medicines sample_data/medicines_sample.csv

echo "Creating initial admin..."
python manage.py create_Admin

echo "Starting Gunicorn..."

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers 1 \
    --threads 4 \
    --timeout 120 \
    --log-level info \
    --error-logfile -