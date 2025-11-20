#!/bin/bash

APP_PORT=${PORT:-8000}
cd /app/

# Run collectstatic
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations (optional, but recommended)
echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

/opt/ENVCRM/bin/gunicorn --worker-tmp-dir /dev/shm base.wsgi:application --bind "0.0.0.0:${APP_PORT}"