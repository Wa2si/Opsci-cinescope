# TME 7 (Kubernetes)

# Plan du TME

1.  Installation environnement
2.  Lancement cluster Kubernetes
3.  Manipulation des Pods
4.  Services Kubernetes
5.  Deployments
6.  Debugging Kubernetes
7.  Configuration YAML
8.  ConfigMap
9.  Scaling
10. Nettoyage

------------------------------------------------------------------------

# Partie 1: Installation

## Question 1

Installer Docker.

``` bash
sudo apt update
sudo apt install docker.io
```

V&eacute;rifier :

``` bash
docker --version
docker run hello-world
```

Question : Que fait la commande `docker run hello-world` ?

------------------------------------------------------------------------

## Question 2

Installer kubectl.

``` bash
sudo snap install kubectl --classic
```

Tester :

``` bash
kubectl version --client
```

Question : A quoi sert kubectl ?

------------------------------------------------------------------------

## Question 3

Installer Minikube.

``` bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

Tester :

``` bash
minikube version
```

------------------------------------------------------------------------

# Partie 2: Configuration proxy
Configurer :

``` bash
export http_proxy=http://proxy:3128
export https_proxy=http://proxy:3128
```

Configurer Docker :

``` bash
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo nano /etc/systemd/system/docker.service.d/http-proxy.conf
```

Ajouter :

    [Service]
    Environment="HTTP_PROXY=http://proxy:3128"
    Environment="HTTPS_PROXY=http://proxy:3128"

Red&eacute;marrer Docker :

``` bash
sudo systemctl daemon-reexec
sudo systemctl restart docker
```

------------------------------------------------------------------------

# Partie 3: Lancer Kubernetes

## Question 4

D&eacute;marrer Minikube.

``` bash
minikube start
```

Si vous obtenez une erreur indiquant qu’un seul processus est disponible alors que Minikube en n&eacute;cessite deux, vous pouvez forcer Minikube &agrave; utiliser un seul processus avec la commande suivante
``` bash
minikube start --cpus=1 --force
```

Afficher les nodes.

``` bash
kubectl get nodes
```

Questions :

-   Combien de nodes voyez-vous ?
-   Quel est leur statut ?

------------------------------------------------------------------------

## Question 5

Afficher les informations du cluster.

``` bash
kubectl cluster-info
```

Question : Quel composant g&egrave;re les requ&ecirc;tes Kubernetes ?

------------------------------------------------------------------------

# Partie 4: Les Pods

## Question 6

Cr&eacute;er un Pod nginx.

``` bash
kubectl run nginx --image=nginx
```

Lister les pods.

``` bash
kubectl get pods
```

Questions :

-   Quel est le statut du pod ?
-   Combien de conteneurs contient-il ?

------------------------------------------------------------------------

## Question 7

Inspecter le Pod.

``` bash
kubectl describe pod nginx
```

Questions :

-   Sur quel node est-il ex&eacute;cut&eacute; ?
-   Quelle image Docker utilise-t-il ?

------------------------------------------------------------------------

## Question 8

Afficher les logs.

``` bash
kubectl logs nginx
```

Question : Que repr&eacute;sentent ces logs ?

------------------------------------------------------------------------

# Partie 5: Services Kubernetes

Un Pod n'est pas accessible depuis l'ext&eacute;rieur.

## Question 9

Cr&eacute;er un service.

``` bash
kubectl expose pod nginx --type=NodePort --port=80
```

Lister les services.

``` bash
kubectl get services
```

Question : Quel port externe a &eacute;t&eacute; attribu&eacute; ?

Acc&eacute;der au service.

``` bash
minikube service nginx
```

------------------------------------------------------------------------

# Partie 6: Deployments

Les Deployments permettent de g&eacute;rer plusieurs pods.

## Question 10

Cr&eacute;er un deployment.

``` bash
kubectl create deployment web --image=nginx
```

Lister les deployments.

``` bash
kubectl get deployments
```

------------------------------------------------------------------------

## Question 11

Scaler l'application.

``` bash
kubectl scale deployment web --replicas=4
```

Lister les pods.

``` bash
kubectl get pods
```

Questions :

-   Combien de pods sont pr&eacute;sents ?
-   Pourquoi leurs noms sont diff&eacute;rents ?

------------------------------------------------------------------------

# Partie 7: Test de r&eacute;silience

## Question 12

Supprimer un pod.

``` bash
kubectl delete pod NOM_DU_POD
```

Observer.

``` bash
kubectl get pods
```

Question : Pourquoi un nouveau pod appara&icirc;t-il ?

------------------------------------------------------------------------

# Partie 8: Debugging Kubernetes

Lister tous les objets.

``` bash
kubectl get all
```

Afficher les &eacute;v&eacute;nements.

``` bash
kubectl get events
```

Question : A quoi servent les events Kubernetes ?

------------------------------------------------------------------------

# Partie 9: Kubernetes YAML

Cr&eacute;er un fichier :

nginx.yaml

``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-yaml
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
    - containerPort: 80
```

Appliquer :

``` bash
kubectl apply -f nginx.yaml
```

Question : Pourquoi Kubernetes utilise-t-il YAML ?

------------------------------------------------------------------------

# Partie 10: ConfigMap

Cr&eacute;er une ConfigMap.

``` bash
kubectl create configmap app-config --from-literal=ENV=dev
```

Lister :

``` bash
kubectl get configmap
```

Question : A quoi sert une ConfigMap ?

------------------------------------------------------------------------

# Partie 11: Scaling avanc&eacute;

Modifier le nombre de replicas.

``` bash
kubectl scale deployment web --replicas=6
```

Observer.

``` bash
kubectl get pods
```

Question : Quel est l'int&eacute;r&ecirc;t du scaling horizontal ?

------------------------------------------------------------------------

# Partie 12: Nettoyage

Supprimer les ressources.

``` bash
kubectl delete deployment web
kubectl delete service nginx
kubectl delete pod nginx
kubectl delete pod nginx-yaml
```

Arr&ecirc;ter Minikube.

``` bash
minikube stop
```

