# Spec — Système de clés BETA (repo WEBSITE / serveur)

> Document destiné à Claude Code, repo **website** (celui qui contient le serveur interrogé par le logiciel).
> Un document jumeau (`BETA_KEYS_SPEC_SOFTWARE.md`) existe pour le repo logiciel. La section 2 (« Contrat d'interface ») est **identique** dans les deux : ne la modifie jamais seul. Si tu penses qu'elle doit changer, signale-le à l'utilisateur au lieu de l'adapter dans ton coin.

---

## 1. Contexte et objectif

Beaver est un logiciel lourd de détection de défauts du bois par IA (modèles YOLO/PyTorch). Pour la phase de beta test Epitech, des étudiants testeurs doivent pouvoir l'utiliser **pendant 2 semaines** sans pouvoir conserver ou partager durablement une copie fonctionnelle.

Principe retenu :

1. Le site distribue des **clés BETA** (format distinct d'une vraie licence).
2. Une clé BETA donne droit, pendant sa durée de validité, à **télécharger** le logiciel puis à l'**activer**.
3. À chaque lancement et périodiquement ensuite, le logiciel interroge ce serveur. Le serveur répond par une **enveloppe signée** (Ed25519) indiquant si la clé est active ou non. **L'heure de référence est celle du serveur, jamais celle de la machine cliente.**
4. Le serveur ne renvoie pas qu'un booléen : quand la clé est active, il renvoie aussi la **clé de déchiffrement des modèles IA** (les poids sont chiffrés dans le binaire distribué). Patcher le `if` côté client ne suffit donc pas pour utiliser les modèles. C'est la protection principale.

Menaces visées : copie conservée après la beta, clé partagée dans un groupe, faux serveur qui répond « actif », rejeu d'une ancienne réponse, horloge reculée. Hors périmètre : extraction mémoire par un attaquant expert (couvert par le contrat de beta test).

## 2. Contrat d'interface (identique dans les deux repos)

### 2.1 Format des clés

- Forme : `BETA-XXXX-XXXX-XXXX-XXXX`, 16 caractères utiles en **Crockford base32** (alphabet `0123456789ABCDEFGHJKMNPQRSTVWXYZ`, sans I, L, O, U), tirés avec un CSPRNG (80 bits d'entropie).
- Regex : `^BETA-[0-9A-HJKMNP-TV-Z]{4}(-[0-9A-HJKMNP-TV-Z]{4}){3}$`
- Normalisation avant tout traitement : trim, majuscules, remplacement des espaces par rien.
- Une vraie licence a un format différent ; ne touche pas à ce format.

### 2.2 Valeurs par défaut (configurables, côté serveur)

| Paramètre | Défaut | Variable d'env |
|---|---|---|
| Durée de validité après 1re activation | 14 jours | `BETA_DURATION_DAYS` |
| Délai pour activer une clé jamais utilisée (`redeem_by`) | 30 jours après création | `BETA_REDEEM_WINDOW_DAYS` |
| Machines max par clé | 2 | `BETA_MAX_MACHINES` |
| Téléchargements max par clé | 5 | `BETA_MAX_DOWNLOADS` |
| Intervalle de revérification demandé au client | 900 s | `BETA_CHECK_INTERVAL_SECONDS` |
| Durée de vie d'un lien de téléchargement | 600 s | `BETA_DOWNLOAD_URL_TTL_SECONDS` |

Sémantique : le compteur de 14 jours démarre à la **première activation réussie** (pas à la création de la clé, pas au téléchargement). Une clé jamais activée expire à `redeem_by`.

### 2.3 Endpoint de validation

`POST /api/beta/validate` — `Content-Type: application/json`

Requête :

```json
{
  "key": "BETA-XXXX-XXXX-XXXX-XXXX",
  "machine_id": "<sha256 hex, 64 caractères>",
  "nonce": "<base64url, 16 à 32 octets aléatoires>",
  "app_version": "1.2.3",
  "platform": "windows | linux | macos",
  "model_key_id": "beta-1"
}
```

- `machine_id` : empreinte déjà hachée côté client (voir 2.6). Le serveur ne reçoit jamais l'identifiant brut.
- `model_key_id` : identifiant de clé de chiffrement lu dans l'en-tête des fichiers modèles embarqués (voir 2.7).
- L'appel enregistre implicitement la machine lors du premier passage (si `max_machines` n'est pas atteint) et démarre le compteur de 14 jours à la toute première activation de la clé.

Réponse HTTP 200 (toujours une enveloppe signée pour les statuts métier) :

```json
{
  "payload": "<base64url(JSON UTF-8, voir ci-dessous)>",
  "signature": "<base64url(signature Ed25519 des octets de la chaîne payload tels quels)>",
  "kid": "2026-11"
}
```

On signe **la chaîne base64url du payload telle quelle** (octets ASCII), ce qui évite toute ambiguïté de canonicalisation JSON. Le client vérifie la signature avant de parser le payload.

Contenu du payload :

```json
{
  "v": 1,
  "status": "active",
  "nonce": "<écho exact du nonce reçu>",
  "machine_id": "<écho>",
  "server_time": "2026-11-21T10:00:00Z",
  "expires_at": "2026-12-05T10:00:00Z",
  "check_after_seconds": 900,
  "model_key_id": "beta-1",
  "model_key": "<base64 de 32 octets, présent uniquement si status = active>",
  "message": "texte optionnel, informatif"
}
```

Dates en UTC, ISO 8601, suffixe `Z`.

Autres codes HTTP (réponses non signées) : `400` requête mal formée, `429` rate limit (avec `Retry-After`), `5xx` erreur serveur. Le client traite `429` et `5xx` comme une indisponibilité temporaire, pas comme une expiration.

### 2.4 Statuts

| `status` | Sens |
|---|---|
| `active` | Clé valide ; `model_key` fourni |
| `expired` | Durée dépassée, ou `redeem_by` dépassé sans activation |
| `revoked` | Révoquée manuellement |
| `invalid` | Clé inconnue |
| `machine_limit` | Nombre max de machines atteint (et cette machine n'est pas déjà enregistrée) |
| `update_required` | `model_key_id` demandé inconnu ou retiré ; le client doit télécharger une version plus récente |

Hors `active`, aucun `model_key` n'est jamais renvoyé.

### 2.5 Endpoint de téléchargement

`POST /api/beta/download`

Requête : `{ "key": "BETA-…", "platform": "windows|linux|macos" }`

Réponse 200 : `{ "url": "<lien signé temporaire>", "filename": "...", "version": "1.2.3", "sha256": "<hex>", "size": 123456789, "expires_in": 600 }`

Réponse 403 : `{ "status": "expired | revoked | invalid" }`. Réponse 404 si aucune release active pour la plateforme. Un lien ne sert qu'une fois si l'infrastructure le permet, sinon il expire après `BETA_DOWNLOAD_URL_TTL_SECONDS`.

### 2.6 Identifiant de machine (rappel, implémenté côté logiciel)

`machine_id = SHA-256("beaver-beta:" + identifiant_machine_brut)` en hexadécimal minuscule. Identifiant brut : `/etc/machine-id` (Linux), `MachineGuid` du registre (Windows), `IOPlatformUUID` (macOS).

### 2.7 Chiffrement des modèles

- Algorithme : AES-256-GCM, clé de 32 octets.
- Fichier chiffré : `<nom_original>.enc` avec le format binaire :
  `magic "BBM1" (4 octets) | longueur de key_id (1 octet) | key_id (ASCII) | nonce (12 octets) | ciphertext || tag (16 octets)`
- AAD (données authentifiées) : `magic || key_id || nom_original (UTF-8, sans le suffixe .enc)`.
- Les clés vivent **uniquement** dans la configuration du serveur (`BETA_MODEL_KEYS`, voir 5.3). Jamais dans un dépôt git, jamais dans le binaire.
- Rotation : on peut chiffrer une nouvelle cohorte de beta avec un nouvel id (`beta-2`) et retirer l'ancien de `BETA_MODEL_KEYS` ; les anciens binaires reçoivent alors `update_required`.

---

## 3. Mission pour ce repo (website)

À livrer, dans l'ordre :

1. Exploration du repo (stack, framework, ORM/BDD, système de migrations, auth admin éventuelle, déploiement, conventions de tests). **Adapte-toi à l'existant** : mêmes outils, mêmes conventions, pas de nouvelle dépendance lourde sans raison.
2. Modèle de données + migrations.
3. Services : génération/validation de clés, signature, gestion des clés de modèles, rate limiting.
4. Endpoints `POST /api/beta/validate` et `POST /api/beta/download` conformes à la section 2.
5. Page web `/beta` (voir 6).
6. CLI d'administration (voir 7).
7. Tests, vecteur de test partagé, documentation courte (`docs/beta-keys.md`).

## 4. Modèle de données

Adapte les types à l'ORM du repo.

**`beta_keys`**
- `id`, `key_hash` (UNIQUE) = `HMAC-SHA256(BETA_KEY_PEPPER, clé_normalisée)` en hex. **La clé en clair n'est jamais stockée.**
- `key_hint` : 4 derniers caractères, pour que l'admin identifie une clé.
- `label` : nom/email du testeur (texte libre).
- `revoked` (bool), `revoked_at`, `revoke_reason`.
- `created_at`, `redeem_by`, `activated_at` (nullable), `expires_at` (nullable).
- `max_machines`, `max_downloads`, `download_count`.

**`beta_activations`**
- `id`, `key_id` (FK), `machine_hash`, `platform`, `app_version`, `first_seen_at`, `last_seen_at`, `last_ip_truncated` (IPv4 /24, IPv6 /48).
- UNIQUE (`key_id`, `machine_hash`).

**`beta_events`** (journal d'audit)
- `id`, `key_id` (nullable), `type` (`validate_ok`, `validate_denied`, `download_issued`, `key_created`, `key_revoked`, `rate_limited`…), `at`, `ip_truncated`, `details` (JSON court, jamais de clé ni de model_key).

**`beta_releases`**
- `id`, `platform`, `version`, `storage_path`, `sha256`, `size`, `is_active`, `created_at`.

Statut calculé (fonction unique, très testée) :

```
si revoked                                -> revoked
sinon si activated_at est NULL et now > redeem_by -> expired
sinon si expires_at non NULL et now >= expires_at  -> expired
sinon                                     -> active
```

## 5. Logique serveur

### 5.1 Validation (`/api/beta/validate`)

1. Valider le schéma de la requête (taille max des champs, regex de la clé, `machine_id` = 64 hex, `nonce` base64url de 16 à 32 octets). Sinon `400`.
2. Appliquer le rate limiting (5.4) avant tout accès BDD coûteux.
3. Normaliser la clé, calculer son HMAC, chercher en base. Inconnue : réponse signée `status: invalid` (même temps de réponse approximatif).
4. Calculer le statut. Si non `active` : réponse signée avec ce statut, journaliser, fin.
5. **Transaction atomique** (attention aux courses) :
   - Si `activated_at` est NULL : `UPDATE … SET activated_at = now, expires_at = now + durée WHERE id = ? AND activated_at IS NULL`.
   - Si la machine est déjà dans `beta_activations` : mettre à jour `last_seen_at`, `app_version`.
   - Sinon, si le nombre de machines `< max_machines` : insérer ; sinon réponse signée `machine_limit`.
6. Résoudre `model_key_id` dans `BETA_MODEL_KEYS`. Absent : `update_required`.
7. Construire le payload (section 2.3), l'encoder en base64url, signer, répondre. `check_after_seconds` = `BETA_CHECK_INTERVAL_SECONDS`, sans jamais dépasser le temps restant avant `expires_at` (minimum 30 s).

### 5.2 Signature

- Ed25519. Clé privée dans `BETA_SIGNING_PRIVATE_KEY` (base64), identifiant `BETA_SIGNING_KID`. **Jamais dans le repo.**
- Fournis un script de génération de paire de clés qui affiche la clé publique à copier dans le repo logiciel.
- Prévoir la rotation : `kid` dans l'enveloppe, plusieurs clés publiques possibles côté client ; côté serveur une seule clé de signature active à la fois.
- N'expose pas la clé publique par endpoint que le client irait chercher au runtime (elle doit être épinglée dans le binaire).

### 5.3 Configuration (variables d'environnement)

`BETA_KEY_PEPPER`, `BETA_SIGNING_PRIVATE_KEY`, `BETA_SIGNING_KID`, `BETA_MODEL_KEYS` (JSON `{"beta-1":"<base64 32 octets>"}`), plus les paramètres du tableau 2.2. Documente-les dans `.env.example` sans valeurs réelles. Le serveur refuse de démarrer la fonctionnalité si une variable obligatoire manque.

### 5.4 Rate limiting et durcissement

- `/validate` : max 60 requêtes/heure/clé et 30 échecs (`invalid`) / 15 min / IP. Au-delà : `429`.
- `/download` : mêmes principes, plus limite `max_downloads` par clé.
- Comparaisons à temps constant pour tout ce qui touche aux secrets.
- Ne jamais journaliser : clé en clair, `model_key`, `BETA_*` secrets, payload complet.
- HTTPS obligatoire ; pas de CORS permissif sur ces routes (le client est une app native, pas un navigateur).
- Messages d'erreur génériques côté web ; le détail précis (expirée, révoquée) n'est donné qu'avec une clé valide dans la base.

## 6. Page web `/beta`

- Formulaire « Entrez votre clé BETA ». Validation côté serveur (appel interne équivalent à `/download`).
- Clé active : affiche les jours restants (calcul serveur) si elle est déjà activée, sinon « La durée de 14 jours démarre à la première ouverture du logiciel », puis boutons de téléchargement par plateforme avec version et empreinte SHA-256.
- Clé expirée/révoquée/invalide : message clair en français, contact `betatest.beaver@gmail.com`.
- Pas de clé stockée dans l'URL ni dans un cookie persistant ; pas de clé dans les logs d'accès (POST uniquement).
- Reprends le design existant du site.

## 7. CLI d'administration

Pas d'API d'admin publique. Un script/commande (selon les conventions du repo) :

- `beta-keys create --label "Prénom Nom" [--count N] [--days 14] [--max-machines 2]` : affiche les clés en clair **une seule fois** (et propose un export CSV). Sinon elles sont irrécupérables, seul le hash est stocké.
- `beta-keys list` : id, hint, label, statut calculé, `activated_at`, `expires_at`, nombre de machines, nombre de téléchargements, `last_seen_at`.
- `beta-keys show <id>` : détail + machines + derniers événements.
- `beta-keys revoke <id> [--reason "..."]`
- `beta-keys extend <id> --days N` et `beta-keys reset-machines <id>`
- `beta-release register --platform windows --version 1.2.3 --file ./Beaver-beta.zip` : calcule le SHA-256, envoie le fichier vers le stockage **privé**, active la release.
- `beta-crypto gen-signing-key` et `beta-crypto gen-model-key --id beta-1` (affiche la valeur à mettre dans `BETA_MODEL_KEYS` et celle à passer au script de chiffrement du repo logiciel).

Stockage des binaires : privé (jamais dans `public/`, jamais dans git). Lien signé temporaire : soit les URL présignées du stockage objet si le projet en utilise un, soit une route du serveur qui vérifie un jeton HMAC à durée limitée avant de streamer le fichier.

## 8. Vecteur de test partagé

Génère `docs/beta/test-vector.json` contenant : une paire de clés Ed25519 **de test explicitement marquée comme telle**, un exemple de requête, et l'enveloppe signée correspondante (payload `active`, plus une variante `expired`). L'utilisateur le copiera dans le repo logiciel pour que ses tests de vérification de signature s'appuient sur la même référence. Ne jamais utiliser cette paire en production.

## 9. Tests attendus

- Statut calculé : actif, expiré (durée), expiré (`redeem_by` sans activation), révoqué ; bornes à la seconde près.
- Activation atomique : deux requêtes simultanées sur une clé neuve ne fixent `activated_at` qu'une fois.
- Limite de machines : 3e machine refusée, machine déjà connue acceptée, `reset-machines`.
- Signature : l'enveloppe se vérifie avec la clé publique ; le nonce et le `machine_id` sont bien en écho ; le `model_key` n'est jamais présent hors `active`.
- `model_key_id` inconnu → `update_required`.
- Rate limiting et `429`.
- Les clés en clair n'apparaissent ni en base ni dans les logs.
- Téléchargement : lien expiré refusé, compteur `max_downloads` respecté, clé expirée refusée.

## 10. Définition de « terminé »

- [ ] Migrations appliquées, modèles et services en place.
- [ ] `/api/beta/validate` et `/api/beta/download` conformes à la section 2.
- [ ] Page `/beta` fonctionnelle.
- [ ] CLI d'admin complète, clés en clair affichées une seule fois.
- [ ] `.env.example` et `docs/beta-keys.md` à jour (variables, procédure de rotation, procédure de publication d'une release).
- [ ] Tests verts, vecteur de test généré.
- [ ] Aucun secret dans le dépôt (vérifie avec `git grep` sur `BETA_`).

## 11. Points à ne pas faire

- Ne pas faire dépendre la validité de l'heure fournie par le client.
- Ne pas renvoyer `model_key` hors statut `active`.
- Ne pas stocker les clés BETA en clair, ni les journaliser.
- Ne pas modifier le système de vraies licences existant.
- Ne pas modifier la section 2 sans l'accord de l'utilisateur (le logiciel en dépend).
