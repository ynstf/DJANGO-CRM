#!/bin/bash
APP_PORT=${PORT:-8000}
cd /app/
/opt/ENVCRM/bin/gunicorn --worker-tmp-dir /dev/shm base.wsgi:application --bind "0.0.0.0:${APP_PORT}"