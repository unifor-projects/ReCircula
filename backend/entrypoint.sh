#!/bin/sh
set -e

echo "Running Alembic migrations..."
uv run alembic upgrade head

echo "Starting Uvicorn server..."
exec uv run uvicorn app.asgi:socket_app --host 0.0.0.0 --port 8000 --reload
