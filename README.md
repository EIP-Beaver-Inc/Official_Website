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
