#!/bin/bash
# script de deploiement sur minikube
# lance minikube si besoin, build les images, applique les manifests
set -e

echo "=== Deploiement Cinescope K8s ==="

# 1. demarre minikube si il tourne pas deja
if ! minikube status &>/dev/null; then
  echo "[1/7] Demarrage de Minikube..."
  minikube start --cpus=1 --force
else
  echo "[1/7] Minikube deja en route"
fi

# 2. activation de metrics-server pour l'autoscaling (HPA)
echo "[2/7] Activation de metrics-server..."
minikube addons enable metrics-server

# 3. on switch sur le docker de minikube pour que les images soient dispo dans le cluster
echo "[3/7] Switch vers le Docker de Minikube..."
eval $(minikube docker-env)

# 4. build des images dans le docker de minikube
echo "[4/7] Build image backend..."
docker build -t films-backend:latest ../backend/

echo "[5/7] Build image frontend..."
docker build -t films-frontend:latest ../frontend/

# 6. on applique tous les manifests k8s
echo "[6/7] Application des manifests..."
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
kubectl apply -f backend-hpa.yaml
kubectl apply -f frontend-hpa.yaml

# 7. on attend que tout soit pret
echo "[7/7] Attente des pods..."
kubectl -n cinescope rollout status deployment/backend --timeout=60s
kubectl -n cinescope rollout status deployment/frontend --timeout=60s

echo ""
echo "=== Deploiement termine ==="
kubectl -n cinescope get pods
kubectl -n cinescope get services
kubectl -n cinescope get hpa
echo ""
echo "URL de l'app:"
minikube service frontend -n cinescope --url
