# HEF History Portal — production image
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_BASE_DIR=/usr/src/backend \
    DJANGO_STATIC_ROOT=/var/www/static \
    DJANGO_MEDIA_ROOT=/var/www/media \
    GUNICORN_PORT=8000 \
    GUNICORN_WORKERS=2 \
    GUNICORN_TIMEOUT=60

WORKDIR /usr/src/backend

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend/ /usr/src/backend/
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && mkdir -p /var/www/static /var/www/media /data/History

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
