#!/bin/bash
# lance toute la stack (postgres + back + front) avec docker-compose
# une seule commande pour demarrer le projet
set -e

cd "$(dirname "$0")"

# charge le .env si present (pour TMDB_API_KEY)
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

echo "Mode: TMDB $([ -n "$TMDB_API_KEY" ] && echo 'live' || echo 'mock')"
echo "Front : http://localhost:8080"
echo "API   : http://localhost:8000"

docker compose up --build
