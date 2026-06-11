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
