# Beaver — Official Website

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) et Docker Compose

## Lancer l'application

```bash
docker compose up --build
```

L'application est accessible sur **http://localhost**.

Pour arrêter :

```bash
docker compose down
```

## Envoi des emails (formulaires Contact & Devis)

Chaque message du formulaire **Contact** et chaque **demande de devis** est enregistré
en base puis envoyé par email à `beaver.eip@gmail.com` (en-tête `Reply-To` = l'email du
visiteur : il suffit de cliquer sur « Répondre » dans Gmail).

L'envoi passe par le SMTP de Gmail avec un **mot de passe d'application** :

1. Sur le compte `beaver.eip@gmail.com`, activer la **validation en 2 étapes**
   (https://myaccount.google.com/security).
2. Créer un mot de passe d'application : https://myaccount.google.com/apppasswords
   (nom : « Site Beaver »). Google affiche un code de 16 caractères.
3. Ajouter dans le `.env` à la racine (ou `backend/.env` en local) :

```env
SMTP_USER=beaver.eip@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
# Optionnel :
# NOTIFY_EMAIL_TO=beaver.eip@gmail.com,autre@exemple.fr
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# FORM_RATE_LIMIT=5              # envois max par IP…
# FORM_RATE_WINDOW_SECONDS=600   # …sur cette fenêtre
```

4. `docker compose up -d --build backend`

Sans `SMTP_USER`/`SMTP_PASSWORD`, les formulaires fonctionnent toujours (stockage en base)
mais aucun email n'est envoyé (un avertissement est loggé). Le statut d'envoi est stocké
dans le champ `email_status` (`sent` / `failed` / `disabled`) de chaque document.

## Devis, commandes et licences

Le parcours client se pilote depuis l'onglet **Commandes** de la page admin :

1. **Demande de devis** : le formulaire « Demander un devis » du site crée un dossier « Nouveau ».
2. **Envoyer un devis** : montant HT, détail, validité, **durée de la licence** (1, 2, 3 ans ou
   sans limite) et **nombre de postes** ; le client le reçoit par mail et répond à ce mail pour
   commander (copie de chaque envoi dans la boîte Beaver).
3. **Commande reçue : livrer** : à cliquer quand le client a donné son accord. La livraison part
   **automatiquement** : le site émet la **licence signée** aux conditions du devis (la durée court
   à partir de ce jour), ouvre son **espace client** et lui envoie un mail avec le lien de
   téléchargement de l'installateur et sa licence. **Une seule clé** : la licence (`BVR1.…`) active
   le logiciel et connecte aussi à l'espace client (menu « Espace client », `/beta`). Les anciennes
   clés d'accès (`XXXX-XXXX-XXXX-XXXX`, bêta-testeurs) restent acceptées.
4. Si la livraison n'a pas pu partir (aucun installateur publié, clé de signature absente), le
   dossier reste « Commande reçue » avec la raison ; une fois corrigé, **Livrer** la relance (et
   permet aussi des conditions particulières). « Renvoyer le mail » refait un envoi avec un lien neuf.

Le client télécharge aussi l'installateur et retrouve sa licence dans son espace client.

Configuration (dans le `.env` à la racine) :

```env
# Clé privée de signature des licences. SECRÈTE, à sauvegarder hors du serveur :
# sans elle, impossible d'émettre une licence que le logiciel accepte.
# Générer : python backend/licensing.py generate (affiche aussi la clé publique à
# reporter dans Beaver/frontend/services/licence.py).
LICENCE_PRIVATE_KEY=...
SITE_URL=https://beaver-website.fr   # pour les liens envoyés par mail
DOWNLOAD_LINK_DAYS=30                # validité d'un lien de téléchargement
```

Publier une version du logiciel : copier `BeaverSetup-x.y.z.exe` (construit par
`Beaver/installer/build-installer.ps1`) dans le dossier `releases/` à côté de
`docker-compose.yml`. La plus haute version est servie.

Tests du serveur (sans MongoDB ni SMTP) : `cd backend && pytest tests`.

## Tester tout le système en local (sans la prod, sans Docker)

```powershell
powershell -ExecutionPolicy Bypass -File dev\run_local.ps1     # -Rebuild après une modif du frontend
```

Le site complet tourne sur **http://localhost:8001** (admin : `/admin`, mot de passe =
`ADMIN_TOKEN` du `.env`, sinon `admin-local`) :

- base MongoDB simulée en mémoire, vide à chaque lancement ;
- les mails ne partent pas : ils sont enregistrés dans `outbox/` (fichiers `.eml`) ;
- l'installateur servi est celui de `../Beaver/installer/dist` ;
- la configuration des tests est lue dans **`.env.test-local`** (ignoré par git), le `.env`
  gardant la clé de prod ; sans ce fichier, c'est le `.env`. Les licences y sont signées avec une
  clé de **test** (le script refuse la clé de prod). Paire de test :
  `.venv-dev\Scripts\python.exe backend\licensing.py generate`, à mettre dans `.env.test-local`
  avec `ADMIN_TOKEN` et, pour `-VraisMails`, `SMTP_USER` / `SMTP_PASSWORD`.

Parcours automatique (devis → commande → livraison → mail → téléchargement → espace
client → licence acceptée par le logiciel), le site local étant lancé :

```powershell
.venv-dev\Scripts\python.exe dev\parcours_local.py
```

Le bandeau affiché au lancement donne la commande pour démarrer BEAVER installé avec la
clé publique de test.

## Développement local (sans Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Créer un fichier `backend/.env` :

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=beaver_db
```

Lancer le serveur :

```bash
python server.py
```

Le backend tourne sur **http://localhost:8001**.

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm start
```

Créer un fichier `frontend/.env` :

```env
VITE_BACKEND_URL=http://localhost:8001
```

Le frontend tourne sur **http://localhost:5173**.

## Structure

```
.
├── backend/      # API FastAPI + MongoDB
├── frontend/     # React + Vite
└── docker-compose.yml
```
