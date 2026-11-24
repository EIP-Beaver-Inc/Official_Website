"""Le parcours client complet contre le site local lancé par dev\\run_local.ps1 :
demande de devis -> devis -> commande -> livraison -> mail -> téléchargement
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
    for ligne in (SITE / ".env").read_text(encoding="utf-8").splitlines():
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
               json={"amount_ht": 4500, "details": "Licence 1 an", "validity_days": 15})
    r.raise_for_status()
    assert "4 500,00 € HT" in texte(dernier_mail(debut, client_mail))
    etape("devis envoyé au client (4 500,00 € HT)")

    # 3. Le client accepte : commande
    c.post(f"/api/admin/requests/{rid}/status", headers=admin, json={"status": "commande"}).raise_for_status()
    etape("commande enregistrée")

    # 4. Livraison : licence signée, clé d'accès, lien de téléchargement par mail
    debut = time.time() - 1
    r = c.post(f"/api/admin/requests/{rid}/deliver", headers=admin,
               json={"licence_expires": "2027-12-31", "seats": 1})
    r.raise_for_status()
    livre = r.json()
    mail = texte(dernier_mail(debut, client_mail))
    assert livre["licence_key"] in mail and livre["access_key"] in mail
    lien = re.search(r"https?://\S+/api/download/[\w-]+", mail).group(0)
    etape(f"livraison : licence {livre['licence_key'][:12]}..., mail au client avec le lien")

    # 5. Le lien du mail télécharge l'installateur
    with c.stream("GET", lien.replace("http://localhost:8001", URL)) as d:
        d.raise_for_status()
        taille = sum(len(b) for b in d.iter_bytes())
    nom = re.search(r'filename="?([^";]+)', d.headers["content-disposition"]).group(1)
    attendu = (BEAVER / "installer" / "dist" / nom).stat().st_size
    assert taille == attendu, (taille, attendu)
    etape(f"téléchargement : {nom} ({taille // 2**20} Mo), identique au fichier publié")

    # 6. L'espace client avec la clé d'accès du mail
    r = c.post("/api/beta/validate", json={"key": livre["access_key"], "company": "Scierie Test 日本",
                                            "contact_name": "Élodie Łukasz", "email": client_mail})
    r.raise_for_status()
    auth = {"Authorization": f"Bearer {r.json()['session_token']}"}
    lic = c.get("/api/beta/licence", headers=auth).json()["licence"]
    assert lic["key"] == livre["licence_key"]
    assert "/api/download/" in c.get("/api/beta/download", headers=auth).json()["url"]
    etape("espace client : licence et téléchargement disponibles")

    # 7. Le logiciel accepte cette licence (son propre code, clé publique de test)
    os.environ["BEAVER_LICENCE_PUBLIC_KEY"] = _env("BEAVER_LICENCE_PUBLIC_KEY") or ""
    if not os.environ["BEAVER_LICENCE_PUBLIC_KEY"]:
        sys.path.insert(0, str(SITE / "backend"))
        os.environ["LICENCE_PRIVATE_KEY"] = _env("LICENCE_PRIVATE_KEY")
        import licensing
        os.environ["BEAVER_LICENCE_PUBLIC_KEY"] = licensing.public_key_b64()
    sys.path.insert(0, str(BEAVER / "frontend"))
    from services.licence import verify
    l = verify(livre["licence_key"])
    assert l.customer == "Scierie Test 日本" and l.seats == 1
    etape(f"le logiciel BEAVER accepte la licence : {l.customer}, {l.expires_text()}")

    print("\nParcours complet OK.")


if __name__ == "__main__":
    main()
