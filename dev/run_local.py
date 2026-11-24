"""Le site complet en local, pour tester sans la prod (ni Docker, ni MongoDB, ni SMTP).

- Base : MongoDB simulée en mémoire (mongomock-motor), vide à chaque lancement.
- Mails : enregistrés dans outbox/ (fichiers .eml à ouvrir avec Outlook ou
  Thunderbird), jamais envoyés.
- Licences : signées avec la clé de TEST du .env ; le script refuse la clé de prod.
- Versions : l'installateur servi est celui de ../Beaver/installer/dist.
- Le frontend construit (frontend/dist) est servi par le même serveur, sur
  http://localhost:8001 : les liens des mails (espace client, téléchargement)
  marchent tels quels.

Lancement : dev\\run_local.ps1 (prépare l'environnement puis appelle ce fichier).
"""
from __future__ import annotations

import base64
import os
import re
import sys
import time
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
BACKEND = SITE / "backend"
BEAVER = Path(os.environ.get("BEAVER_REPO", SITE.parent / "Beaver")).resolve()
OUTBOX = SITE / "outbox"
PORT = int(os.environ.get("PORT", "8001"))
VRAIS_MAILS = "--vrais-mails" in sys.argv   # dev\run_local.ps1 -VraisMails


def _lire_env(fichier: Path) -> dict[str, str]:
    valeurs = {}
    if fichier.exists():
        for ligne in fichier.read_text(encoding="utf-8").splitlines():
            cle, sep, val = ligne.strip().partition("=")
            if sep and cle and not cle.startswith("#"):
                valeurs[cle.strip()] = val.strip().strip('"').strip("'")
    return valeurs


def _cle_publique_de_prod() -> str | None:
    """La clé publique embarquée dans le logiciel = celle de la prod."""
    source = BEAVER / "frontend" / "services" / "licence.py"
    if not source.exists():
        return None
    trouve = re.search(r'^PUBLIC_KEY\s*=\s*"([^"]+)"', source.read_text(encoding="utf-8"), re.M)
    return trouve.group(1) if trouve else None


def configurer() -> dict[str, str]:
    env = _lire_env(SITE / ".env")
    if not env.get("LICENCE_PRIVATE_KEY"):
        sys.exit("LICENCE_PRIVATE_KEY manque dans .env : génère une paire de TEST avec\n"
                 "  .venv-dev\\Scripts\\python.exe backend\\licensing.py generate")
    os.environ.update({
        "LICENCE_PRIVATE_KEY": env["LICENCE_PRIVATE_KEY"],
        "MONGO_URL": "mongodb://memoire",          # remplacé par la base en mémoire
        "DB_NAME": "beaver_local",
        "ADMIN_TOKEN": env.get("ADMIN_TOKEN") or "admin-local",
        "CORS_ORIGINS": "*",
        "SITE_URL": f"http://localhost:{PORT}",
        "RELEASES_DIR": str(BEAVER / "installer" / "dist"),
        "DOWNLOAD_LINK_DAYS": env.get("DOWNLOAD_LINK_DAYS", "30"),
    })
    if VRAIS_MAILS:
        # Envoi réel par le SMTP du .env (Gmail Beaver), une copie reste dans outbox/.
        if not (env.get("SMTP_USER") and env.get("SMTP_PASSWORD")):
            sys.exit("-VraisMails : SMTP_USER et SMTP_PASSWORD manquent dans .env\n"
                     "(mot de passe d'application Gmail, voir la section « Envoi des emails » du README).")
        for cle in ("SMTP_USER", "SMTP_PASSWORD", "SMTP_HOST", "SMTP_PORT", "SMTP_FROM", "NOTIFY_EMAIL_TO"):
            if env.get(cle):
                os.environ[cle] = env[cle]
    else:
        # Faux identifiants : le mailer se croit configuré, l'envoi va dans outbox/.
        os.environ.update({"SMTP_USER": "beaver.local@example.com", "SMTP_PASSWORD": "local",
                           "NOTIFY_EMAIL_TO": "beaver.local@example.com"})
    sys.path.insert(0, str(BACKEND))
    import licensing

    publique = licensing.public_key_b64()
    if publique == _cle_publique_de_prod():
        sys.exit("ARRÊT : la LICENCE_PRIVATE_KEY du .env est la clé de PROD.\n"
                 "Pour les tests, génère une paire de test (backend\\licensing.py generate)\n"
                 "et garde la clé de prod uniquement sur le serveur et dans ta sauvegarde.")
    return {"publique": publique, "admin": os.environ["ADMIN_TOKEN"]}


def brancher_memoire_et_outbox() -> None:
    # Base : Motor remplacé par mongomock-motor AVANT l'import de server.py.
    import mongomock_motor
    import motor.motor_asyncio
    motor.motor_asyncio.AsyncIOMotorClient = mongomock_motor.AsyncMongoMockClient

    # Mails : écrits dans outbox/ au lieu de partir par SMTP.
    import mailer
    OUTBOX.mkdir(exist_ok=True)

    envoi_reel = mailer._send_sync

    def vers_outbox(cfg, msg) -> None:
        sujet = re.sub(r"[^\w\- ]+", "", str(msg["Subject"]))[:60].strip() or "mail"
        nom = f"{time.strftime('%Y%m%d-%H%M%S')}-{sujet}.eml"
        (OUTBOX / nom).write_bytes(bytes(msg))
        if VRAIS_MAILS:
            envoi_reel(cfg, msg)
            print(f"  [mail ENVOYÉ] {msg['To']} : {msg['Subject']}", flush=True)
        else:
            print(f"  [mail] {msg['To']} : {msg['Subject']}  ->  outbox\\{nom}", flush=True)

    mailer._send_sync = vers_outbox


def servir_le_frontend(app) -> None:
    """frontend/dist sur la même adresse, avec retour sur index.html (routes React)."""
    from fastapi.responses import FileResponse

    dist = SITE / "frontend" / "dist"
    if not (dist / "index.html").exists():
        sys.exit("frontend/dist manque : dev\\run_local.ps1 le construit (npm run build).")

    @app.get("/{chemin:path}", include_in_schema=False)
    async def page(chemin: str):
        fichier = (dist / chemin).resolve()
        if chemin and fichier.is_file() and dist in fichier.parents:
            return FileResponse(fichier)
        return FileResponse(dist / "index.html")


def main() -> None:
    infos = configurer()
    brancher_memoire_et_outbox()
    os.chdir(BACKEND)
    import server   # noqa: E402 - après les remplacements ci-dessus
    servir_le_frontend(server.app)

    dist = Path(os.environ["RELEASES_DIR"])
    versions = sorted(p.name for p in dist.glob("BeaverSetup-*.exe")) if dist.exists() else []
    print(f"""
=====================================================================
 Site BEAVER en local (base en mémoire, vide à chaque lancement)
   Site        : http://localhost:{PORT}
   Admin       : http://localhost:{PORT}/admin   mot de passe : {infos['admin']}
   Mails       : {"ENVOYÉS pour de vrai (copie dans " + str(OUTBOX) + ")" if VRAIS_MAILS else OUTBOX}
   Installateur: {versions[-1] if versions else 'AUCUN dans ' + str(dist)}

 Logiciel installé, avec la clé de TEST (dans un PowerShell) :
   $env:BEAVER_LICENCE_PUBLIC_KEY = "{infos['publique']}"
   & "$env:LOCALAPPDATA\\Programs\\BEAVER\\beaver-launcher.exe"
=====================================================================
""", flush=True)

    import uvicorn
    uvicorn.run(server.app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
