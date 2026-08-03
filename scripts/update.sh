#!/usr/bin/env bash
# Pull latest code from GitHub and rebuild/restart Docker stack on the Ubuntu server.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.caddy.yml}"
BRANCH="${BRANCH:-main}"

echo "==> git fetch / pull ($BRANCH)"
git fetch origin
git pull --ff-only origin "$BRANCH"

echo "==> docker compose up -d --build ($COMPOSE_FILE)"
if [[ -n "${MY_DOMAIN:-}" ]]; then
  MY_DOMAIN="$MY_DOMAIN" docker compose -f "$COMPOSE_FILE" up -d --build
else
  docker compose -f "$COMPOSE_FILE" up -d --build
fi

echo "==> done. Containers:"
docker compose -f "$COMPOSE_FILE" ps
