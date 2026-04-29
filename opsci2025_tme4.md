# Introduction au CI/CD avec GitLab

## Objectifs du TME

L'objectif de ce TME est d'introduire les concepts de l'int&eacute;gration et du d&eacute;ploiement continus (CI/CD) en utilisant GitLab CI/CD. 

&Agrave; la fin du TME, vous serez capables de :

- Comprendre le fonctionnement de GitLab CI/CD.
- Mettre en place un pipeline CI/CD simple.
- Automatiser des tests et le d&eacute;ploiement d'une application.
- Utiliser des runners GitLab.

---

## Plan du TME 

#### 1. Introduction au CI/CD et GitLab CI/CD 

#### 2. Mise en place d'un projet GitLab 

#### 3. Cr&eacute;ation d'un premier pipeline GitLab 

#### 4. Ajout d'un test automatis&eacute; dans le pipeline 

#### 5. Introduction aux runners et ex&eacute;cution en local

---

## Ressources

- Documentation GitLab CI/CD : [GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
- Tutoriel GitLab CI/CD : [Tutoriel GitLab](https://docs.gitlab.com/ee/tutorials/)

---

## Travail attendu

&Agrave; la fin du TME, chaque &eacute;tudiants devra :

1. Avoir un d&eacute;p&ocirc;t GitLab fonctionnel avec un fichier `.gitlab-ci.yml`.
2. Avoir un pipeline CI/CD d&eacute;clench&eacute; automatiquement &agrave; chaque push.
3. Int&eacute;grer au moins un test automatis&eacute; dans le pipeline.
4. Avoir un job de d&eacute;ploiement.

---
---

## 1. Pr&eacute;sentation du CI/CD et son importance

- CI (Continuous Integration) : Automatisation des tests et validation du code &agrave; chaque modification.
- CD (Continuous Deployment) : Automatisation du d&eacute;ploiement apr&egrave;s validation des tests.
- Avantages : D&eacute;tection rapide des erreurs, am&eacute;lioration de la qualit&eacute; du code, gain de temps dans le d&eacute;veloppement.

### **Fonctionnement des pipelines dans GitLab**

- Un pipeline est une s&eacute;quence de jobs ex&eacute;cut&eacute;s automatiquement &agrave; chaque commit ou d&eacute;clenchement manuel.
- Un pipeline est d&eacute;fini via un fichier `.gitlab-ci.yml`.
- Il comprend plusieurs &eacute;tapes (`stages`) qui regroupent les t&acirc;ches (`jobs`).

### **Explication des concepts : jobs, stages, runners**

- **Jobs** : T&acirc;ches ex&eacute;cut&eacute;es dans le pipeline (tests, compilation, d&eacute;ploiement, etc.).
- **Stages** : Groupes de jobs qui s'ex&eacute;cutent de mani&egrave;re s&eacute;quentielle.
- **Runners** : Agents d'ex&eacute;cution qui ex&eacute;cutent les jobs du pipeline sur des machines locales ou distantes.

----
----

## 2. Mise en place d'un projet GitLab
### **Objectif**
L'objectif de cette partie est d'obtenir un d&eacute;p&ocirc;t GitLab bien configur&eacute; qui respecte certaines bonnes pratiques de s&eacute;curit&eacute;, notamment :

- **Interdire les pushs directs sur la branche `main`**.
- **Obliger l'utilisation de merge requests (MR) pour int&eacute;grer du code dans la branche `main`**.
- **Activer la protection des branches pour &eacute;viter les modifications involontaires**.
- **Configurer des permissions d'acc&egrave;s adapt&eacute;es aux membres de l'&eacute;quipe**.

---

### **Cr&eacute;ation d'un d&eacute;p&ocirc;t GitLab**
1. Connectez-vous &agrave; [GitLab](https://gitlab.com/).
2. Cliquez sur **`New Project`** puis **`Create Blank Project`**.
3. Donnez un nom &agrave; votre projet et choisissez une visibilit&eacute; (**Priv&eacute;e** ou **Publique**).
4. Cliquez sur **`Create Project`**.

---

### Configuration des r&egrave;gles de s&eacute;curit&eacute;
1. Allez dans **`Settings` &rarr; `Repository`**.
2. Dans la section **`Protected Branches`**, s&eacute;lectionnez la branche **`main`** et appliquez les r&egrave;gles suivantes :
   - **Interdiction des pushs directs sur `main`** (**Allowed to push and merge=No one**).
   - **Obligation de passer par une Merge Request (MR) pour fusionner du code**.
3. Activez les pipelines CI/CD en allant dans **`Settings` &rarr; `CI/CD` &rarr; `Enable shared runners`**.

---

### Ajout d'un projet : Portfolio avec un serveur Python
Maintenant que votre d&eacute;p&ocirc;t GitLab est bien configur&eacute;, nous allons ajouter une **simple page web g&eacute;r&eacute;e par un serveur Python**. Cette page permet d'afficher un **portfolio**.

#### Qu'est-ce qu'un portfolio ?
Un **portfolio web** est une page qui pr&eacute;sente des informations sur une personne (nom, comp&eacute;tences, exp&eacute;riences, liens vers ses projets, etc.). Il est souvent utilis&eacute; par les &eacute;tudiants et les professionnels pour montrer leurs r&eacute;alisations.

Vous pouvez t&eacute;l&eacute;charger le projet complet contenant le **HTML, CSS, JavaScript et le serveur Python** via ce lien :

[T&eacute;l&eacute;charger le projet](tme4/opsci2025_tme4.zip)

---

### Ajout du projet dans votre d&eacute;p&ocirc;t GitLab
1. **Acc&eacute;dez au dossier du projet** :
   ```sh
   cd chemin/vers/votre/projet (TME4)
   ```
2. **Initialisez un d&eacute;p&ocirc;t Git**:
   ```sh
   git init
   ```
3. **Ajoutez l'origine distante avec l'URL de votre d&eacute;p&ocirc;t GitLab** :
   ```sh
   git remote add origin "lien-vers-votre-depot"
   ```
4. **Cr&eacute;ez une nouvelle branche** pour travailler sur votre projet (car `main` est prot&eacute;g&eacute;) :
   ```sh
   git checkout -b feature-portfolio
   ```
5. **Ajoutez les fichiers du projet** :
   ```sh
   git add .
   ```
6. **Faites un commit avec un message explicite** :
   ```sh
   git commit -m "Ajout du projet Portfolio avec serveur Python"
   ```
7. **Poussez la branche vers GitLab** :
   ```sh
   git push origin feature-portfolio
   ```

---

#### Configuration de l'authentification avec un token d'acc&egrave;s
La premi&egrave;re fois que vous effectuez un `git push`, GitLab vous demandera un **nom d'utilisateur et un token d'acc&egrave;s**.

### **&Eacute;tapes pour configurer un token d'acc&egrave;s** :
1. Allez dans **`Edit profile` &rarr; `Access Tokens`** sur GitLab.
2. Cr&eacute;ez un **Personal Access Token** avec les permissions `write_repository`.
3. Lorsque Git vous demande un mot de passe, entrez ce **token d'acc&egrave;s** &agrave; la place.

Une fois configur&eacute;, votre projet sera bien synchronis&eacute; avec GitLab !

---

### Cr&eacute;ation d'une Merge Request (MR) pour fusionner dans `main`
### ** Qu'est-ce qu'une Merge Request ? **
Une **Merge Request (MR)** est une demande de fusion d'une branche dans `main`. Elle permet de **valider et revoir les changements** avant qu'ils ne soient int&eacute;gr&eacute;s au code principal.

### Cr&eacute;ation d'une Merge Request sur GitLab
1. **Allez sur GitLab**, dans votre projet.
2. **Cliquez sur `Merge Requests` > `New Merge Request`**.
3. S&eacute;lectionnez :
   - **Source branch** : `feature-portfolio`
   - **Target branch** : `main`
4. Ajoutez un **titre et une description** explicatifs.
5. **Cliquez sur `Create Merge Request`**.
6. Une fois valid&eacute;e par un mainteneur, cliquez sur **"Merge"** pour fusionner.

---

### F&eacute;licitations !
Apr&egrave;s avoir fusionn&eacute; la Merge Request, **votre code est maintenant dans la branche `main`** et pr&ecirc;t &agrave; &ecirc;tre d&eacute;ploy&eacute; !

### **Explication du fichier `.gitlab-ci.yml`**

Le fichier `.gitlab-ci.yml` est utilis&eacute; pour d&eacute;finir les pipelines GitLab CI/CD. Il est &eacute;crit en YAML et doit &ecirc;tre plac&eacute; &agrave; la racine du d&eacute;p&ocirc;t.

Exemple minimal :

```yaml
stages:
  - test

job_test:
  stage: test
  script:
    - echo "Ex&eacute;cution des tests"
```

- `stages` : D&eacute;finit les diff&eacute;rentes &eacute;tapes du pipeline.
- `job_test` : Un job qui s'ex&eacute;cute dans l'&eacute;tape `test`.
- `script` : Commandes ex&eacute;cut&eacute;es dans le job.

Ce fichier sera ex&eacute;cut&eacute; automatiquement par GitLab CI/CD d&egrave;s qu'un commit est pouss&eacute; sur une branche active du d&eacute;p&ocirc;t.


## 3. Cr&eacute;ation d'un premier pipeline GitLab (45 min)

### **Objectif**
Dans cette partie, nous allons cr&eacute;er un **pipeline GitLab CI/CD** pour automatiser le d&eacute;ploiement de votre **site web statique** avec **GitLab Pages**.

Nous allons :
- **Comprendre la structure du projet** et le r&ocirc;le de chaque fichier.
- **&Eacute;crire un fichier `.gitlab-ci.yml`** qui g&egrave;re le d&eacute;ploiement du site.
- **D&eacute;clencher un pipeline GitLab** pour publier automatiquement la page.
- **Analyser les logs du pipeline** pour comprendre son fonctionnement.

---

### Structure du projet
Votre projet est organis&eacute; comme suit :

```
/nom_projet (TME4)
|---- .gitlab-ci.yml  # Fichier de configuration du pipeline CI/CD
|---- /simple_app      # Dossier contenant les fichiers du site
|   |---- index.html   # Page principale du site web
|   |---- styles.css   # Feuille de style CSS
|   |---- script.js    # Fichier JavaScript
```

#### **Description des fichiers**
- **`index.html`** &rarr; Fichier principal contenant le code HTML du site.
- **`styles.css`** &rarr; Fichier qui d&eacute;finit le style et la mise en page du site.
- **`script.js`** &rarr; Fichier contenant du code JavaScript pour ajouter des interactions.
- **`.gitlab-ci.yml`** &rarr; Fichier de configuration qui d&eacute;finit le pipeline CI/CD.

---

### **Cr&eacute;ation du fichier `.gitlab-ci.yml`**
### **Votre mission : compl&eacute;ter le fichier pour d&eacute;ployer le site avec GitLab Pages**
Ajoutez un fichier `.gitlab-ci.yml` &agrave; la racine du projet et compl&eacute;tez-le en suivant ces consignes :

1. Le pipeline doit avoir **une seule &eacute;tape** appel&eacute;e `deploy`.
2. Il doit **copier les fichiers** HTML, CSS et JS dans un dossier `public/` (GitLab Pages attend un dossier `public`).
3. Il doit **sp&eacute;cifier les artefacts** pour conserver ces fichiers apr&egrave;s l'ex&eacute;cution du pipeline.
4. Le pipeline ne doit s'ex&eacute;cuter **que sur la branche `main`**.

---

### **Remplissez le fichier `.gitlab-ci.yml`**
Essayez de compl&eacute;ter le fichier en vous basant sur les consignes ci-dessus.  
Une fois que vous avez essay&eacute;, comparez avec la **correction ci-dessous**. 

---

### **Correction du fichier `.gitlab-ci.yml`**
Si vous avez des doutes, voici le fichier `.gitlab-ci.yml` complet :

```yaml
image: alpine:latest

stages:
  - deploy

deploy:
  stage: deploy
  script:
    - mkdir -p public
    - cp simple_app/index.html simple_app/styles.css simple_app/script.js public/
  artifacts:
    paths:
      - public
  only:
    - main
```

---

### **Explication du fichier `.gitlab-ci.yml`**

1. **`image: alpine:latest`**  
   &rarr; Utilise l'image **Alpine Linux**, une distribution l&eacute;g&egrave;re pour ex&eacute;cuter les scripts.

2. **`stages:`**  
   &rarr; D&eacute;finit les diff&eacute;rentes &eacute;tapes du pipeline. Ici, nous avons une seule &eacute;tape : `deploy`.

3. **`deploy:`**  
   &rarr; D&eacute;crit l'&eacute;tape de d&eacute;ploiement.

4. **`stage: deploy`**  
   &rarr; Sp&eacute;cifie que cette &eacute;tape appartient au stage `deploy`.

5. **`script:`**  
   &rarr; Liste les commandes qui seront ex&eacute;cut&eacute;es lors du d&eacute;ploiement :
   - **`mkdir -p public`** &rarr; Cr&eacute;e un dossier `public` si ce n'est pas d&eacute;j&agrave; fait.
   - **`cp simple_app/index.html simple_app/styles.css simple_app/script.js public/`**  
     &rarr; Copie les fichiers web dans le dossier `public`.

6. **`artifacts:`**  
   &rarr; D&eacute;finit les fichiers qui doivent &ecirc;tre conserv&eacute;s apr&egrave;s l'ex&eacute;cution du pipeline.  
   - **`paths: - public`** &rarr; Indique que le dossier `public` doit &ecirc;tre sauvegard&eacute;.

7. **`only: - main`**  
   &rarr; Ce pipeline ne s'ex&eacute;cute **que lorsque du code est pouss&eacute; sur `main`**.

---

### **D&eacute;clenchement automatique du pipeline**
D&egrave;s que vous **push** ou **merge** votre code sur `main`, GitLab va **automatiquement ex&eacute;cuter le pipeline**.

### **&Eacute;tapes :**
1. **Ajoutez le fichier `.gitlab-ci.yml`** :
   ```sh
   git add .gitlab-ci.yml
   git commit -m "Ajout du pipeline GitLab CI/CD"
   ```
2. **Poussez le code sur GitLab** :
   ```sh
   git push origin feature-portfolio
   ```
3. **Allez sur GitLab &rarr; `Build` &rarr; `Pipelines`** pour voir l'ex&eacute;cution en cours.

---

### **Analyse des logs du pipeline**
Une fois le pipeline d&eacute;clench&eacute; :
1. **Allez dans** `Build` &rarr; `Pipelines` &rarr; Cliquez sur le pipeline en cours.
2. **Ouvrez l'&eacute;tape `deploy`** et observez :
   - La cr&eacute;ation du dossier `public`.
   - La copie des fichiers HTML, CSS et JS.
   - La publication des fichiers pour GitLab Pages.


### **F&eacute;licitations !**
Votre site est maintenant **d&eacute;ploy&eacute; avec GitLab Pages** !  

----
----

## 4. Ajout des tests automatis&eacute;s dans le pipeline (45 min)

### **Pourquoi ajouter des tests automatis&eacute;s ?**
Les tests automatis&eacute;s sont essentiels pour garantir la **qualit&eacute;** et la **fiabilit&eacute;** du code.  
Voici les principales raisons de les inclure dans un pipeline **CI/CD** :

**D&eacute;tection pr&eacute;coce des bugs** : Les erreurs sont d&eacute;tect&eacute;es **avant** que le code ne soit d&eacute;ploy&eacute;.  
**Am&eacute;lioration de la stabilit&eacute;** : On &eacute;vite les r&eacute;gressions qui peuvent casser le site.  
**Gain de temps** : Plus besoin de tester manuellement chaque fonctionnalit&eacute;.  
**Facilite la collaboration** : Chaque modification est valid&eacute;e automatiquement, garantissant un code plus sûr.  

---

### **Ajout d'un job de test dans le fichier `.gitlab-ci.yml`**
Nous allons maintenant ajouter un **job de test** dans le pipeline CI/CD.

#### **Votre mission : compl&eacute;ter le fichier `.gitlab-ci.yml`**
Ajoutez un job **`test`** dans `.gitlab-ci.yml` pour **ex&eacute;cuter des tests automatiques**.

##### **Consignes :**
1. Cr&eacute;ez un job **`test`** qui v&eacute;rifie la pr&eacute;sence des fichiers `index.html`, `styles.css` et `script.js`.
2. Utilisez l'image Docker `alpine` pour ex&eacute;cuter le job.
3. Si un fichier est manquant, le pipeline doit &eacute;chouer.

---

### **Descriptif du fichier attendu  `.gitlab-ci.yml`**
1. **`stages: - test - deploy`**  
   &rarr; Ajoute une nouvelle &eacute;tape `test` avant `deploy`.

2. **`test:`**  
   &rarr; D&eacute;finit un job appel&eacute; `test`.

3. **`stage: test`**  
   &rarr; Sp&eacute;cifie que ce job appartient &agrave; l'&eacute;tape `test`.

4. **`script:`**  
   &rarr; Liste les **commandes ex&eacute;cut&eacute;es** lors du test :
     &rarr; V&eacute;rifie si le fichier `index.html` **existe**.  
     &rarr; Si non, le job &eacute;choue (`exit 1`).
   - **M&ecirc;me v&eacute;rification pour `styles.css` et `script.js`**.

5. **`deploy:`**  
   &rarr; Ce job **ne s'ex&eacute;cute que si les tests r&eacute;ussissent**.

---

### **Ex&eacute;cution et validation des tests**
D&egrave;s que vous **push** ou **merge** votre code, **GitLab va ex&eacute;cuter le job de test** avant de d&eacute;ployer le site.

### **&Eacute;tapes &agrave; suivre :**
1. **Cr&eacute;ez une branche pour ajouter votre pipeline :**
   ```sh
   git checkout -b feature-tests
   ```
2. **Ajoutez et validez votre fichier `.gitlab-ci.yml` :**
   ```sh
   git add .gitlab-ci.yml
   git commit -m "Ajout des tests automatis&eacute;s dans la CI/CD"
   ```
3. **Poussez votre branche sur GitLab :**
   ```sh
   git push origin feature-tests
   ```
4. **Cr&eacute;ez une Merge Request (MR) et attendez la validation avant de fusionner (Validez et fusionner)**.

---

### **Analyse des logs du pipeline**
1. **Allez dans `Build` &rarr; `Pipelines` &rarr; Cliquez sur le pipeline en cours.**
2. **Ouvrez l'&eacute;tape `test`** et observez :
   - Si les fichiers HTML, CSS et JS sont bien d&eacute;tect&eacute;s.
   - Si un fichier est **manquant**, le job &eacute;chouera et affichera une erreur.

---

### **Ajout d'un test unitaire avec Jest**
Supposons que les d&eacute;veloppeurs ont ajout&eacute; un **test unitaire** dans le dossier `__tests__/` et qu'ils vous demandent de l'inclure dans le pipeline.

#### **Informations fournies par l'&eacute;quipe :**
- Les tests sont dans `__tests__/`
- Le framework utilis&eacute; est **Jest**
- Pour ex&eacute;cuter les tests, il faut utiliser la commande :
  ```sh
  npm test
  ```
- Jest utilise **`@jest-environment jsdom`**

---

#### **Votre mission : compl&eacute;ter `.gitlab-ci.yml` pour ex&eacute;cuter Jest**
Ajoutez un **job `unit-test`** qui ex&eacute;cute Jest avant le d&eacute;ploiement.

---

### ** `.gitlab-ci.yml` avec Jest**

```yaml
mage: node:18

stages:
  - test
  - unit-test
  - deploy

test:
  stage: test
  script:
    - echo "V&eacute;rification de l'existence des fichiers..."
    # TODO

unit-test:
  # TODO

deploy:
  stage: deploy
  script:
    - mkdir -p public
    - cp simple_app/index.html simple_app/styles.css simple_app/script.js public/
  artifacts:
    paths:
      - public
  only:
    - main
```

---

### **Explication de l'int&eacute;gration de Jest**
- **`unit-test:`** &rarr; Ajoute un job pour ex&eacute;cuter Jest.

---

### **R&egrave;gle d'or : Ne pas merger si les tests &eacute;chouent !**
- V&eacute;rifiez que le pipeline CI/CD passe avec succ&egrave;s.
- Assurez-vous que **toutes les &eacute;tapes (`test`, `unit-test`) sont en vert**.
- Si un test &eacute;choue, **corrigez le bug avant de merger la MR**.

---

## **\o/ F&eacute;licitations ! \o/**
Vous avez ajout&eacute; **des tests de pr&eacute;sence de fichiers et des tests unitaires avec Jest** dans le pipeline CI/CD ! 

Vous ma&icirc;trisez maintenant **GitLab CI/CD avec des tests automatis&eacute;s** !

----
----

# 5. Introduction aux runners et ex&eacute;cution en local (30 min)

##  **Objectif**
Dans cette partie, nous allons d&eacute;couvrir les **runners GitLab**, comprendre leur r&ocirc;le et apprendre &agrave; **ex&eacute;cuter un pipeline en local** avec un **runner d&eacute;di&eacute;**.

Nous allons :
- **Comprendre ce qu'est un runner GitLab et son fonctionnement**.
- **Installer et configurer un runner GitLab en local**.
- **Ex&eacute;cuter un pipeline CI/CD avec un runner d&eacute;di&eacute;**.

---

## **Qu'est-ce qu'un runner GitLab ?**
Un **runner** est un **agent d'ex&eacute;cution** qui ex&eacute;cute les jobs des pipelines GitLab CI/CD.

### **Pourquoi utiliser un runner ?**
- **Automatisation des builds, tests et d&eacute;ploiements**.
- **Ex&eacute;cution des jobs sur diff&eacute;rents environnements** (Docker, machines locales, serveurs).
- **Meilleure gestion des ressources** en r&eacute;partissant la charge entre plusieurs runners.

### **Types de runners GitLab**
| Type de Runner | Description |
|---------------|-------------|
| **Shared Runner** | G&eacute;r&eacute; par GitLab, utilis&eacute; par plusieurs projets. |
| **Group Runner** | Assign&eacute; &agrave; un groupe sp&eacute;cifique de projets GitLab. |
| **Specific Runner** | D&eacute;di&eacute; &agrave; un seul projet GitLab. |
| **Local Runner** | Install&eacute; sur une machine locale pour ex&eacute;cuter des pipelines en local. |

---

## **Installation et configuration d'un runner local**
Nous allons installer et configurer un **runner local** pour ex&eacute;cuter un pipeline CI/CD.

### **&Eacute;tape 1 : Installer GitLab Runner**
1. **Sur Linux (Debian/Ubuntu)**
   ```sh
   sudo curl -L --output /usr/local/bin/gitlab-runner https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64
   sudo chmod +x /usr/local/bin/gitlab-runner
   sudo useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash
   sudo gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner
   sudo gitlab-runner start
   ```

2. **Sur macOS**
   ```sh
   brew install gitlab-runner
   ```

3. **Sur Windows**
   ```powershell
   New-Item -ItemType Directory -Path 'C:\GitLab-Runner'
   Invoke-WebRequest -Uri "https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-windows-amd64.exe" -OutFile "C:\GitLab-Runner\gitlab-runner.exe"
   ```

---

### **&Eacute;tape 2 : Enregistrer le runner**
1. **R&eacute;cup&eacute;rez le token de votre projet GitLab** :
   - Allez dans **`Settings` &rarr; `CI/CD` &rarr; `Runners`**.
   - Cr&eacute;ez un nouveau runner en cliquant sur **`New project runner`** 
   - Donnez-lui le nom **local** et validez la cr&eacute;ation.
   - Une page s'affichera avec plusieurs options: Choisissez votre syst&egrave;me d'exploitation (Linux, macOS, ...) et Copiez la commande d'installation.
   - Pensez &agrave; copiez le **Token d'enregistrement** (--token <Token>).

2. **Enregistrez le runner sur votre machine** :
   ```sh
   sudo gitlab-runner register
   ```
   Suivez les instructions :
   - **URL de GitLab** : `https://gitlab.com/`
   - **Token du projet** : `Votre token`
   - **Description du runner** : `runner-local`
   - **Tags** : `local`
   - **Executor** : `shell` (ou `docker` si vous utilisez Docker)

3. **D&eacute;marrez le runner** :
   ```sh
   sudo gitlab-runner run
   ```

---

### **Ex&eacute;cution d'un pipeline avec un runner d&eacute;di&eacute;**
Une fois le runner install&eacute; et enregistr&eacute;, vous pouvez l'utiliser pour ex&eacute;cuter des jobs.

#### **&Eacute;tape 1 : Modifier `.gitlab-ci.yml` pour utiliser le runner local**
Ajoutez **`tags: [local]`** dans le fichier `.gitlab-ci.yml` :

```yaml
test:
  stage: test
  script:
    - echo "V&eacute;rification de l'existence des fichiers..."
    # Fait en partie 4
  tags:
    - local
```

#### **&Eacute;tape 2 : Push le code sur gitlab**

---

### **V&eacute;rification et analyse des logs**
1. **Allez sur GitLab &rarr; `Votre branch`**.
2. **V&eacute;rifiez que le job `test` s'ex&eacute;cute sur votre runner local**.

---

### **Bonnes pratiques avec les runners GitLab**
- **Utilisez des runners sp&eacute;cifiques pour optimiser les ressources**.
- **Utilisez Docker comme executor pour des environnements isol&eacute;s**.
- **Ne partagez pas vos tokens de runner en public**.

---

### **F&eacute;licitations !**
Vous avez install&eacute;, configur&eacute; et ex&eacute;cut&eacute; un **runner GitLab en local** pour ex&eacute;cuter vos pipelines CI/CD !

