#!/bin/sh
set -e

cd "${DJANGO_BASE_DIR:-/usr/src/backend}"

echo "Waiting for database..."
python <<'PY'
import os, sys, time
host = os.environ.get("POSTGRES_HOST", "").strip()
if not host:
    sys.exit(0)
import socket
port = int(os.environ.get("POSTGRES_PORT", "5432") or 5432)
for i in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            print("Database is reachable.")
            sys.exit(0)
    except OSError:
        time.sleep(1)
print("Database not reachable after 60s", file=sys.stderr)
sys.exit(1)
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
