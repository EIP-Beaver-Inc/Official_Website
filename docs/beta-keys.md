# Clés BETA du logiciel Beaver (côté serveur)

Implémentation de `BETA_KEYS_SPEC_WEBSITE.md` (contrat partagé avec le repo logiciel, section 2).
Code : [`backend/beta_license/`](../backend/beta_license/). Tests : [`backend/tests/`](../backend/tests/).

> **Deux systèmes distincts.** Ce module (clés `BETA-XXXX-XXXX-XXXX-XXXX`, logiciel) est indépendant du
> **portail beta** du site (clés `XXXX-XXXX-XXXX-XXXX`, espace `/account` : tutoriels, tickets, feedback,
> génération dans `/admin`). Le portail utilise les collections `beta_keys` / `beta_clients` et l'endpoint
> `POST /api/beta/register` (anciennement `/api/beta/validate`, renommé pour laisser ce chemin au contrat logiciel).

## Endpoints

| Route | Appelant | Rôle |
|---|---|---|
| `POST /api/beta/validate` | logiciel | Enveloppe signée Ed25519 (spec 2.3), active la clé au 1er appel |
| `POST /api/beta/download` | page `/beta` (ou logiciel) | Lien temporaire à usage unique (spec 2.5) |
| `GET /api/beta/files/<jeton>` | navigateur | Stream du binaire après vérif. HMAC + expiration + usage unique |
| `POST /api/beta/key-info` | page `/beta` | Statut, jours restants, releases (ne consomme pas de téléchargement) |

- Erreurs de schéma → `400`. Rate limit → `429` + `Retry-After`. Fonction désactivée (variable manquante) → `503`.
- `max_downloads` atteint → `429` `{"detail": "download_limit"}` (la spec range cette limite dans le rate limiting, 5.4).
- Pas de CORS sur `/validate` et `/files/` ; sur `/download` et `/key-info`, CORS uniquement pour les origines
  explicites de `CORS_ORIGINS` (`*` ignoré).
- Le `model_key_id` est vérifié **avant** l'activation : un binaire obsolète reçoit `update_required` sans démarrer
  les 14 jours ni consommer de machine.
- base64url **sans padding** pour `payload` et `signature` ; `model_key` en base64 standard (spec 2.3).

## Données (MongoDB)

Pas de migrations SQL : les index sont créés (idempotent) au démarrage du backend et par `bin/beta-db init`.

| Collection | Contenu |
|---|---|
| `beta_license_keys` | `key_hash` (HMAC-SHA256 pepper, unique), `key_hint`, `label`, `revoked*`, `created_at`, `redeem_by`, `activated_at`, `expires_at`, `duration_days`, `max_machines`, `machine_count`, `max_downloads`, `download_count` |
| `beta_activations` | unique (`key_id`, `machine_hash`), plateforme, version, `first/last_seen_at`, IP tronquée (/24, /48) |
| `beta_events` | journal d'audit (jamais de clé ni de `model_key`) |
| `beta_releases` | `platform`, `version`, `filename`, `storage_path`, `sha256`, `size`, `is_active` |
| `beta_download_tokens` | jetons de téléchargement (usage unique, supprimés par TTL à expiration) |

Le Mongo du compose est une instance seule (sans transactions multi-documents). L'atomicité vient de mises à jour
conditionnelles : `activated_at` n'est fixé que par `update … WHERE activated_at IS NULL`, et une place machine est
réservée par `$inc` conditionnel (`machine_count < max_machines`) + index unique.

Les binaires sont dans le volume Docker privé `beta_releases` (`/data/beta-releases`), jamais dans `public/` ni git.

## Mise en service (VPS)

```bash
# 1. Générer les secrets (afficher, copier dans .env, ne jamais commiter)
docker compose exec backend bin/beta-crypto gen-pepper
docker compose exec backend bin/beta-crypto gen-signing-key --kid 2026-11
docker compose exec backend bin/beta-crypto gen-model-key --id beta-1
# 2. Renseigner BETA_* dans .env (voir .env.example), puis
docker compose up -d --build backend frontend
docker compose logs backend | grep "BETA license"     # doit dire "enabled"
```

- **Clé publique** (`public_key_b64` / `hex` affichée par `gen-signing-key`) → à épingler dans le repo logiciel avec son `kid`.
- **Clé de modèle** (`key_b64` / `hex` de `gen-model-key`) → à passer au script de chiffrement du repo logiciel
  (secret : pas dans git là-bas non plus).
- Le `BETA_KEY_PEPPER` ne doit **jamais** changer une fois des clés émises (toutes deviendraient invalides).

## Administration (CLI, pas d'API d'admin)

Dans le conteneur : `docker compose exec backend bin/beta-keys …` (ou `python -m beta_license.cli beta-keys …`).

```bash
bin/beta-keys create --label "Prénom Nom" [--count N] [--days 14] [--max-machines 2] [--max-downloads 5] \
                     [--redeem-days 30] [--csv /tmp/keys.csv]   # clés en clair affichées UNE SEULE fois
bin/beta-keys list
bin/beta-keys show <id|préfixe d'id|hint 4 car.>
bin/beta-keys revoke <id> [--reason "..."]
bin/beta-keys extend <id> --days N        # activée : repousse expires_at ; jamais activée : repousse redeem_by
bin/beta-keys reset-machines <id>
bin/beta-release register --platform windows --version 1.2.3 --file /tmp/Beaver-beta.zip
bin/beta-release list
bin/beta-db init
```

Le CSV (droits `600`) contient des clés en clair : l'envoyer puis le supprimer
(`docker compose exec backend rm /tmp/keys.csv`).

### Publier une release

```bash
docker compose cp ./Beaver-beta-1.2.3-win.zip backend:/tmp/
docker compose exec backend bin/beta-release register --platform windows --version 1.2.3 --file /tmp/Beaver-beta-1.2.3-win.zip
docker compose exec backend rm /tmp/Beaver-beta-1.2.3-win.zip
```

La nouvelle release devient la seule active pour sa plateforme. Les SHA-256 sont affichés sur `/beta`.

## Rotation

- **Clé de signature** : `gen-signing-key --kid <nouveau>` ; publier d'abord une version du logiciel qui connaît
  les deux clés publiques (ancien et nouveau `kid`), puis remplacer `BETA_SIGNING_PRIVATE_KEY` / `BETA_SIGNING_KID`
  et redémarrer. Une seule clé de signature est active côté serveur.
- **Clé de modèles** (nouvelle cohorte) : `gen-model-key --id beta-2`, chiffrer les modèles avec, ajouter
  `"beta-2"` à `BETA_MODEL_KEYS` (en gardant `beta-1` le temps de la transition), publier la release, puis retirer
  `beta-1` : les anciens binaires reçoivent `update_required`.

## Vecteur de test partagé

[`docs/beta/test-vector.json`](beta/test-vector.json) : paire Ed25519 **de test uniquement**, requête d'exemple,
enveloppes `active` et `expired`, et un cas falsifié qui doit échouer. Déterministe :
`python -m beta_license.cli beta-crypto test-vector --out ../docs/beta/test-vector.json` (un test vérifie que le
fichier commité est à jour). À copier dans le repo logiciel.

## Tests

```bash
cd backend
pytest tests                                         # tests unitaires (sans base)
docker run -d --rm -p 127.0.0.1:27999:27017 mongo:7
MONGO_TEST_URL=mongodb://127.0.0.1:27999 pytest tests   # + tests HTTP/MongoDB (bases jetables)
```

## Limites connues

- Rate limiting en mémoire (un seul processus backend) : remis à zéro au redémarrage.
- Liens de téléchargement à usage unique : une reprise de téléchargement interrompu nécessite un nouveau lien
  (et consomme un téléchargement).
