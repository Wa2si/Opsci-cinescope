#!/bin/bash
# supprime toutes les ressources k8s du projet
set -e

echo "=== Suppression Cinescope K8s ==="

kubectl delete namespace cinescope --ignore-not-found

echo "Ressources supprimees."
echo ""
echo "Pour arreter minikube completement:"
echo "  minikube stop"
