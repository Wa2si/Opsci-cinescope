#!/bin/bash
# deploiement complet sur minikube
set -e

echo " Deploiement Cinescope K8s "

# 1. demarre minikube si besoin
if ! minikube status &>/dev/null; then
  echo "[1/8] Demarrage de Minikube..."
  minikube start --cpus=2 --memory=2048 --force
else
  echo "[1/8] Minikube deja en route"
fi

# 2. metrics-server pour le HPA
echo "[2/8] Activation metrics-server..."
minikube addons enable metrics-server

# 3. ingress controller (nginx)
echo "[3/8] Activation ingress..."
minikube addons enable ingress

# 4. on bascule sur le docker de minikube
echo "[4/8] Switch vers le Docker de Minikube..."
eval $(minikube docker-env)

# 5. build des images localement (pas de registry necessaire)
echo "[5/8] Build backend..."
docker build -t films-backend:latest ../backend/
echo "[6/8] Build frontend..."
docker build -t films-frontend:latest ../frontend/

# 7. application des manifests
echo "[7/8] Application des manifests..."
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f postgres-pvc.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f postgres-service.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
kubectl apply -f backend-hpa.yaml
kubectl apply -f frontend-hpa.yaml

# attente que le webhook ingress-nginx soit pret avant d'appliquer l'ingress
# (le pod peut etre Ready avant que le service webhook accepte les requetes)
echo "Attente du webhook ingress-nginx..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=180s
# retry jusqu'a 6 fois (le webhook met parfois ~30s a s'enregistrer)
for i in {1..6}; do
  if kubectl apply -f ingress.yaml 2>/dev/null; then
    echo "Ingress applique"
    break
  fi
  echo "Webhook pas encore pret, retry dans 10s... ($i/6)"
  sleep 10
done

# 8. on attend que tout soit pret
echo "[8/8] Attente des pods..."
kubectl -n cinescope rollout status deployment/postgres --timeout=120s
kubectl -n cinescope rollout status deployment/backend  --timeout=120s
kubectl -n cinescope rollout status deployment/frontend --timeout=60s

echo ""
echo " Deploiement termine "
kubectl -n cinescope get pods
kubectl -n cinescope get services
kubectl -n cinescope get hpa
kubectl -n cinescope get ingress

echo ""
echo "Pour acceder via Ingress : ajouter une ligne dans /etc/hosts"
echo "  $(minikube ip)  cinescope.local"
echo "puis ouvrir http://cinescope.local"
echo ""
echo "Sinon (acces NodePort frontend direct) :"
minikube service frontend -n cinescope --url
