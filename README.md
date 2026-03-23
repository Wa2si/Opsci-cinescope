# Cinescope — Catalogue de Films

Application web full-stack de catalogue de films avec FastAPI.

## Architecture

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Frontend   │──────▶│   Backend    │──────▶│  TMDB API    │
│  (nginx:80)  │ HTTP  │ (FastAPI:8000)│ HTTP │  (externe)   │
└──────────────┘       └──────┬───────┘       └──────────────┘
                              │
                              ▼ (si pas de clé)
                       ┌──────────────┐
                       │  Mock Data   │
                       │  (20 films)  │
                       └──────────────┘
```

## Demarrage rapide

### Sans cle TMDB (donnees mockees)

```bash
docker-compose up --build
```

Ouvrir http://localhost:8080 dans le navigateur.

### Avec cle TMDB

Creer un fichier `.env` a la racine :

```
TMDB_API_KEY=votre_cle_ici
```

Puis relancer :

```bash
docker-compose up --build
```

### Mode mono-conteneur (backend seul)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Ouvrir http://localhost:8000 — le backend sert directement le frontend depuis `static/index.html`.

## Structure du projet

```
project/
├── backend/
│   ├── main.py              # API FastAPI (routes /hello, /movies, /)
│   ├── requirements.txt     # Dependances Python
│   ├── Dockerfile           # Image Python 3.11-slim
│   ├── test_main.py         # Tests pytest
│   ├── .env.example         # Template de configuration
│   └── static/
│       └── index.html       # Frontend embarque (mode mono-conteneur)
├── frontend/
│   ├── index.html           # Page principale
│   ├── style.css            # Styles premium (dark theme, glassmorphism)
│   ├── script.js            # Logique fetch + rendu dynamique
│   └── Dockerfile           # Image nginx:alpine
├── docker-compose.yml       # Orchestration des 2 services
├── .gitlab-ci.yml           # Pipeline CI/CD (test, build, deploy)
├── k8s/                     # Manifests Kubernetes (TME 7)
│   ├── namespace.yaml       # Namespace cinescope
│   ├── configmap.yaml       # Configuration (TMDB_API_KEY, ENV)
│   ├── backend-deployment.yaml   # Deployment backend (2 replicas)
│   ├── backend-service.yaml      # Service ClusterIP backend
│   ├── frontend-deployment.yaml  # Deployment frontend (2 replicas)
│   ├── frontend-service.yaml     # Service NodePort frontend (30080)
│   ├── deploy.sh            # Script de deploiement complet
│   └── teardown.sh          # Script de nettoyage
└── README.md
```

## Commandes Docker utiles

```bash
# Build et lancement
docker-compose up --build

# Lancement en arriere-plan
docker-compose up -d

# Voir les logs
docker-compose logs -f
docker-compose logs backend
docker-compose logs frontend

# Arreter les services
docker-compose down

# Rebuild un seul service
docker-compose build backend

# Inspecter un conteneur
docker inspect films-backend

# Executer une commande dans un conteneur
docker exec -it films-backend sh

# Stats des conteneurs
docker stats
```

## Variables d'environnement

| Variable       | Description                          | Defaut        |
|---------------|--------------------------------------|---------------|
| `TMDB_API_KEY` | Cle API TMDB (v4 bearer token)      | _(vide = mock)_ |

## Endpoints API

| Methode | Route              | Description                       |
|---------|-------------------|-----------------------------------|
| GET     | `/hello`          | Health check + mode (tmdb/mock)   |
| GET     | `/movies?limit=N` | Liste des films (1 <= N <= 100)   |
| GET     | `/search?q=X`     | Recherche par titre/genre/realisateur |
| GET     | `/`               | Frontend embarque (mono-conteneur)|

## CI/CD

Le pipeline GitLab CI comprend 3 stages :

1. **test** : Execute `pytest` sur les endpoints du backend
2. **build** : Construit les images Docker `films-backend` et `films-frontend`
3. **deploy** : Deploiement simule (echo)

## Kubernetes (TME 7)

Deploiement de l'application sur un cluster Minikube.

### Architecture K8s

```
┌─ Namespace: cinescope ──────────────────────────────────┐
│                                                          │
│  ┌─ Deployment: frontend ──┐  ┌─ Deployment: backend ──┐│
│  │  Pod (nginx)            │  │  Pod (FastAPI)          ││
│  │  Pod (nginx)            │  │  Pod (FastAPI)          ││
│  └────────┬────────────────┘  └────────┬────────────────┘│
│           │                            │                 │
│  ┌────────▼────────────┐  ┌────────────▼──────────────┐  │
│  │ Service: frontend   │  │ Service: backend          │  │
│  │ NodePort :30080     │  │ ClusterIP :8000           │  │
│  └─────────────────────┘  └───────────────────────────┘  │
│                                                          │
│  ┌─ ConfigMap: cinescope-config ──────────────────────┐  │
│  │ ENV=production  TMDB_API_KEY=...                   │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Deploiement rapide

```bash
cd k8s
./deploy.sh
```

Le script :
1. Demarre Minikube si besoin
2. Build les images dans le Docker de Minikube
3. Applique tous les manifests
4. Attend que les pods soient ready
5. Affiche l'URL d'acces

### Commandes K8s utiles

```bash
# Voir tous les objets du namespace
kubectl -n cinescope get all

# Logs d'un pod backend
kubectl -n cinescope logs -l tier=backend

# Scaler le backend a 4 replicas
kubectl -n cinescope scale deployment backend --replicas=4

# Voir les events (debug)
kubectl -n cinescope get events --sort-by='.lastTimestamp'

# Acceder au frontend
minikube service frontend -n cinescope

# Nettoyage complet
./teardown.sh
```

### Concepts K8s utilises

| Concept | Utilisation dans le projet |
|---------|---------------------------|
| **Namespace** | Isolation des ressources dans `cinescope` |
| **Deployment** | Gestion des replicas backend (2) et frontend (2) |
| **Service ClusterIP** | Communication interne backend (non expose) |
| **Service NodePort** | Acces externe au frontend sur le port 30080 |
| **ConfigMap** | Injection de `TMDB_API_KEY` et `ENV` |
| **Probes** | `readinessProbe` et `livenessProbe` sur `/hello` |
| **Resources** | Limites CPU/memoire par conteneur |
| **Scaling** | `kubectl scale` pour ajuster les replicas |
