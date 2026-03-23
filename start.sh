#!/bin/bash
# lance le backend en chargeant automatiquement le .env
cd "$(dirname "$0")/backend"
export $(grep -v '^#' ../.env | xargs)
echo "Mode: TMDB $([ -n "$TMDB_API_KEY" ] && echo 'live' || echo 'mock')"
echo "http://localhost:8000"
uvicorn main:app --host 0.0.0.0 --port 8000
