# Cinescope — Catalogue de Films

Application web full-stack de catalogue de films (FastAPI + PostgreSQL + nginx),
conteneurisée Docker et déployable sur Kubernetes.

## Architecture

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend   │─────▶│   Backend    │─────▶│  PostgreSQL  │
│  nginx :8080 │ HTTP │ FastAPI :8000│ SQL  │     :5432    │
└──────────────┘      └──────┬───────┘      └──────────────┘
                             │
                             ▼ (rafraichissement /h)
                      ┌──────────────┐
                      │  TMDB API    │  ← fallback mock si pas de cle
                      └──────────────┘
```

## Demarrage rapide

Tout se lance avec une commande :

```bash
./start.sh        # ou : docker compose up --build
```

Puis ouvrir http://localhost:8080.

### Avec une cle TMDB (optionnel)

Pour basculer du mode mock vers les vrais films TMDB, créer un `.env` à la racine :

```
TMDB_API_KEY=votre_cle_v4_bearer
```

Et relancer.

## Stack technique

| Couche | Choix | Justification |
|---|---|---|
| Front | HTML/CSS/JS vanilla | Pas de build, sert directement par nginx, suffisant pour ce périmètre |
| Back | FastAPI (Python 3.11) | Async natif, OpenAPI auto-généré, courbe d'apprentissage rapide |
| BDD | PostgreSQL 16 | SQL relationnel standard, large adoption pro, persistance via volume |
| Conteneurisation | Docker + Compose | 3 services orchestrés (db, back, front) |
| Orchestration | Kubernetes (Minikube) | Pods, Services, Ingress, ConfigMap, Secret, HPA |
| CI/CD | GitLab CI | 3 stages (test → build → deploy), JUnit, push vers Registry |

## Endpoints API

| Méthode | Route | Description |
|---|---|---|
| GET | `/hello` | Health check + mode (tmdb/mock) |
| GET | `/status` | Uptime, films en BDD, état général |
| GET | `/movies?limit=N` | Liste des films (1 ≤ N ≤ 100) |
| GET | `/movie/{id}` | Détail d'un film (cast, trailer, etc.) |
| GET | `/search?q=X` | Recherche par titre/réalisateur/genre |
| GET | `/export/movies.json` | Export JSON (téléchargement) |
| GET | `/export/movies.csv` | Export CSV (téléchargement) |

Documentation interactive : http://localhost:8000/docs (Swagger UI auto-généré).

## Structure du projet

```
.
├── backend/                # API FastAPI + tests
│   ├── main.py
│   ├── test_main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # SPA légère
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── Dockerfile
├── k8s/                    # Manifests Kubernetes
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── postgres-{deployment,service,pvc}.yaml
│   ├── backend-{deployment,service,hpa}.yaml
│   ├── frontend-{deployment,service,hpa}.yaml
│   ├── ingress.yaml
│   ├── deploy.sh
│   └── teardown.sh
├── docs/                   # Génération du rapport PDF
│   ├── gen_diagrams.py
│   ├── gen_rapport.py
│   └── rapport_cinescope.pdf
├── docker-compose.yml
├── .gitlab-ci.yml
├── start.sh
└── README.md
```

## Tests

Le backend a 11 tests pytest. Pour les lancer en local il faut une Postgres
joignable (le `docker compose up db` suffit) :

```bash
docker compose up -d db
cd backend
pip install -r requirements.txt
pytest test_main.py -v
```

En CI/CD, GitLab démarre automatiquement un conteneur `postgres:16-alpine`
en service du job de test.

## Déploiement Kubernetes

```bash
cd k8s
./deploy.sh
```

Le script :
1. Démarre Minikube si besoin
2. Active les addons `metrics-server` (HPA) et `ingress` (nginx)
3. Build les images dans le Docker de Minikube
4. Applique tous les manifests
5. Affiche l'URL à utiliser (Ingress sur `cinescope.local` ou NodePort)

Pour utiliser l'Ingress, ajouter dans `/etc/hosts` :
```
<minikube_ip>  cinescope.local
```

### Concepts K8s utilisés

| Concept | Rôle dans le projet |
|---|---|
| Namespace | Isolation dans `cinescope` |
| Deployment | 2 replicas back, 2 replicas front, 1 replica db |
| Service ClusterIP | Communication interne back ↔ db |
| Service NodePort | Exposition front (fallback sans Ingress) |
| Ingress (nginx) | Point d'entrée unique, routage `/api` ↔ backend |
| ConfigMap | Variables non sensibles (DB_HOST, DB_NAME, ENV) |
| Secret | Variables sensibles (DB_PASSWORD, TMDB_API_KEY) |
| PersistentVolumeClaim | Persistance des données Postgres |
| HPA | Autoscaling 2-5 replicas back, 2-4 front (cible 70% CPU) |
| Probes | Readiness + liveness sur `/hello` (back), `pg_isready` (db) |

## CI/CD

Pipeline GitLab à 3 stages :
1. **test** — pytest sur le backend (avec Postgres en service), rapport JUnit
2. **build** — build des images Docker, push vers GitLab Container Registry
3. **deploy** — simulation de déploiement (uniquement sur `main`)

## Nettoyage

```bash
docker compose down -v       # supprime aussi le volume postgres
cd k8s && ./teardown.sh      # supprime tout le namespace
```
