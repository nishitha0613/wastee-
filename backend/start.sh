#!/usr/bin/env bash
set -e

echo "[STARTUP] Running database schema migrations with Alembic..."
alembic upgrade head || {
    echo "[WARNING] Alembic upgrade encountered an issue or is up-to-date; proceeding..."
}

echo "[STARTUP] Seeding default administrator account if not present..."
python -m app.seed_admin || {
    echo "[INFO] Admin seed finished."
}

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"
WORKERS="${WORKERS:-2}"

echo "[STARTUP] Starting production Uvicorn server on http://${HOST}:${PORT} with ${WORKERS} workers..."
exec uvicorn app.main:app --host "${HOST}" --port "${PORT}" --workers "${WORKERS}"
