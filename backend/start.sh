#!/bin/sh
set -e

# Ensure data directory exists for SQLite volume mount
mkdir -p /app/data

# Run database migrations if available
if [ -d "/app/migrations" ]; then
  echo "Running database migrations (flask db upgrade)..."
  flask db upgrade || echo "Flask db upgrade failed or no migrations to apply."
fi

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 wsgi:app

