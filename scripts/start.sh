#!/usr/bin/env bash
set -euo pipefail

# Optional entrypoint for container or simple PaaS
python manage.py collectstatic --noinput
python manage.py migrate --noinput
exec gunicorn klinika_project.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-3} --timeout 60
