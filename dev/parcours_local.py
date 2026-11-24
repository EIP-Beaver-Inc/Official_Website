"""Le parcours client complet contre le site local lancé par dev\\run_local.ps1 :
demande de devis -> devis -> commande (livrée automatiquement) -> mail -> téléchargement
-> espace client -> licence vérifiée par le code du logiciel BEAVER.

  .venv-dev\\Scripts\\python.exe dev\\parcours_local.py
Code de sortie 0 si tout est bon. Aucune donnée de prod, aucun mail envoyé.
"""
from __future__ import annotations

import email
import os
import re
import sys
import time
from email import policy
from pathlib import Path

import httpx

SITE = Path(__file__).resolve().parent.parent
BEAVER = Path(os.environ.get("BEAVER_REPO", SITE.parent / "Beaver")).resolve()
URL = os.environ.get("SITE_LOCAL", "http://localhost:8001")
OUTBOX = SITE / "outbox"


def _env(cle: str) -> str:
    fichier = SITE / ".env.test-local" if (SITE / ".env.test-local").exists() else SITE / ".env"
    for ligne in fichier.read_text(encoding="utf-8").splitlines():
        k, _, v = ligne.strip().partition("=")
        if k == cle:
            return v.strip()
    return ""


def etape(texte: str) -> None:
    print(f"[OK] {texte}", flush=True)


def dernier_mail(depuis: float, destinataire: str) -> email.message.EmailMessage:
    for _ in range(50):
        for f in sorted(OUTBOX.glob("*.eml"), key=lambda p: p.stat().st_mtime, reverse=True):
            if f.stat().st_mtime < depuis:
                break
            msg = email.message_from_bytes(f.read_bytes(), policy=policy.default)
            if destinataire in str(msg["To"]):
                return msg
        time.sleep(0.1)
    sys.exit(f"[X] aucun mail pour {destinataire} dans {OUTBOX}")


def texte(msg) -> str:
    corps = msg.get_body(preferencelist=("plain", "html"))
    return corps.get_content() if corps else ""


def main() -> None:
    admin = {"X-Admin-Token": _env("ADMIN_TOKEN") or "admin-local"}
    client_mail = f"test+{int(time.time())}@scierie-test.fr"
    c = httpx.Client(base_url=URL, timeout=30)

    # 1. Le client demande un devis depuis le site
    debut = time.time() - 1
    r = c.post("/api/demo-requests", json={
        "nom": "Élodie Łukasz", "entreprise": "Scierie Test 日本", "email": client_mail,
        "telephone": "0600000000", "taille_scierie": "PME", "volume": "200 planches/h",
        "message": "Test local"})
    r.raise_for_status()
    rid = r.json()["id"]
    dernier_mail(debut, "beaver.local@example.com")
    etape("demande de devis enregistrée, notification à Beaver dans outbox/")

    # 2. L'admin envoie le devis
    debut = time.time() - 1
    r = c.post(f"/api/admin/requests/{rid}/quote", headers=admin,
               json={"amount_ht": 4500, "details": "Installation sur site", "validity_days": 15,
                     "licence_months": 12, "seats": 1})
    r.raise_for_status()
    devis = texte(dernier_mail(debut, client_mail))
    assert "4 500,00 € HT" in devis and "Licence : 1 an, 1 poste." in devis
    etape("devis envoyé au client (4 500,00 € HT, licence 1 an, 1 poste)")

    # 3. Le client accepte : « Commande reçue », et la livraison part toute seule
    debut = time.time() - 1
    r = c.post(f"/api/admin/requests/{rid}/status", headers=admin, json={"status": "commande"})
    r.raise_for_status()
    livre = r.json()
    assert livre.get("delivered"), livre.get("delivery_error")
    mail = texte(dernier_mail(debut, client_mail))
    assert livre["licence_key"] in mail and livre["access_key"] in mail
    lien = re.search(r"https?://\S+/api/download/[\w-]+", mail).group(0)
    assert mail.count(livre["licence_key"]) == 1, "la licence, une fois"
    assert not re.search(r"\b[A-Z0-9]{4}(-[A-Z0-9]{4}){3}\b", mail), "aucune autre clé dans le mail"
    etape(f"commande reçue -> livrée automatiquement : licence {livre['licence_key'][:12]}... "
          "(une seule clé) et lien envoyés au client")

    # 4. Le lien du mail télécharge l'installateur
    with c.stream("GET", lien.replace("http://localhost:8001", URL)) as d:
        d.raise_for_status()
        taille = sum(len(b) for b in d.iter_bytes())
    nom = re.search(r'filename="?([^";]+)', d.headers["content-disposition"]).group(1)
    attendu = (BEAVER / "installer" / "dist" / nom).stat().st_size
    assert taille == attendu, (taille, attendu)
    etape(f"téléchargement : {nom} ({taille // 2**20} Mo), identique au fichier publié")

    # 5. L'espace client, avec la même clé : la licence
    r = c.post("/api/beta/login", json={"key": livre["licence_key"]})
    r.raise_for_status()
    auth = {"Authorization": f"Bearer {r.json()['session_token']}"}
    lic = c.get("/api/beta/licence", headers=auth).json()["licence"]
    assert lic["key"] == livre["licence_key"]
    assert "/api/download/" in c.get("/api/beta/download", headers=auth).json()["url"]
    etape("espace client ouvert avec la licence : licence et téléchargement disponibles")

    # 6. Le logiciel accepte cette licence (son propre code, clé publique de test)
    os.environ["BEAVER_LICENCE_PUBLIC_KEY"] = _env("BEAVER_LICENCE_PUBLIC_KEY") or ""
    if not os.environ["BEAVER_LICENCE_PUBLIC_KEY"]:
        sys.path.insert(0, str(SITE / "backend"))
        os.environ["LICENCE_PRIVATE_KEY"] = _env("LICENCE_PRIVATE_KEY")
        import licensing
        os.environ["BEAVER_LICENCE_PUBLIC_KEY"] = licensing.public_key_b64()
    sys.path.insert(0, str(BEAVER / "frontend"))
    from services.licence import verify
    l = verify(livre["licence_key"])
    assert l.customer == "Scierie Test 日本" and l.seats == 1 and l.expires is not None
    etape(f"le logiciel BEAVER accepte la licence : {l.customer}, {l.expires_text()}")

    print("\nParcours complet OK.")


if __name__ == "__main__":
    main()
