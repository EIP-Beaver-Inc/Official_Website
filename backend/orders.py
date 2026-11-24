"""Du devis à la livraison du logiciel.

Un dossier part d'une demande de devis du site (collection `demo_requests`)
et avance ainsi :

    nouveau ──► devis_envoye ──► commande ──► livre
       └──────────────┴──────────────┴──────► annule

- devis_envoye : l'équipe saisit le montant et le détail ; le client reçoit
  le devis par mail et répond à ce mail pour commander (l'échange de mails se
  fait dans la boîte Beaver, qui reçoit une copie de chaque envoi).
- commande : l'équipe a reçu l'accord du client. La livraison part aussitôt,
  toute seule, avec la durée de licence et le nombre de postes du devis.
- livre : le site émet la licence signée (licensing.py), crée la clé d'accès
  à l'espace client (le même mécanisme que les clés beta) et un lien de
  téléchargement de l'installateur, puis envoie le tout au client.
  Si la livraison automatique échoue (pas d'installateur publié, clé de
  signature absente), le dossier reste « commande » avec la raison, et le
  bouton « Livrer » la relance.

L'installateur est un fichier BeaverSetup-<version>.exe déposé dans
RELEASES_DIR ; le plus récent est servi. Un lien de téléchargement est valable
DOWNLOAD_LINK_DAYS jours (30 par défaut) ; l'espace client en recrée un à la
demande.
"""
from __future__ import annotations

import logging
import os
import re
import secrets
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Awaitable, Callable, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

import licensing
from mailer import send_customer_email

logger = logging.getLogger("beaver.orders")

STATUSES = ["nouveau", "devis_envoye", "commande", "livre", "annule"]
RELEASE_PATTERN = re.compile(r"^BeaverSetup-(\d+)\.(\d+)\.(\d+)\.exe$")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def site_url() -> str:
    return os.environ.get("SITE_URL", "https://beaver-website.fr").rstrip("/")


def releases_dir() -> Path:
    return Path(os.environ.get("RELEASES_DIR", "/releases"))


def link_days() -> int:
    try:
        return max(1, int(os.environ.get("DOWNLOAD_LINK_DAYS", "30")))
    except ValueError:
        return 30


def latest_release() -> Optional[Path]:
    """Le BeaverSetup-x.y.z.exe de plus haute version, ou None."""
    folder = releases_dir()
    if not folder.is_dir():
        return None
    found = []
    for f in folder.iterdir():
        m = RELEASE_PATTERN.match(f.name)
        if m and f.is_file():
            found.append((tuple(int(x) for x in m.groups()), f))
    return max(found)[1] if found else None


def release_version(path: Path) -> str:
    m = RELEASE_PATTERN.match(path.name)
    return ".".join(m.groups()) if m else ""


# ====================== Modèles ======================
class QuoteIn(BaseModel):
    amount_ht: float = Field(gt=0, le=1_000_000)
    details: str = Field(min_length=1, max_length=4000)
    validity_days: int = Field(default=30, ge=1, le=365)
    # Ce que la livraison émettra : durée de la licence en mois (None : sans
    # limite), à compter de la livraison, et nombre de postes.
    licence_months: Optional[int] = Field(default=12, ge=1, le=120)
    seats: int = Field(default=1, ge=1, le=100)


DEFAULT_TERMS = {"licence_months": 12, "seats": 1}   # dossier commandé sans devis


def add_months(start: date, months: int) -> date:
    """La même date `months` mois plus tard (le 31 devient le dernier jour du mois)."""
    total = start.month - 1 + months
    year, month = start.year + total // 12, total % 12 + 1
    for day in (start.day, 30, 29, 28):
        try:
            return date(year, month, day)
        except ValueError:
            continue
    raise ValueError(start)


def licence_terms(months: Optional[int], seats: int) -> str:
    duration = "sans limite de durée" if not months else (
        f"{months // 12} an{'s' if months >= 24 else ''}" if months % 12 == 0 else f"{months} mois")
    return f"{duration}, {seats} poste{'s' if seats > 1 else ''}"


class StatusIn(BaseModel):
    status: str


class DeliverIn(BaseModel):
    # None : licence sans limite de durée.
    licence_expires: Optional[date] = None
    seats: int = Field(default=1, ge=1, le=100)
    # Nom inscrit dans la licence (affiché par le logiciel) ; par défaut l'entreprise.
    customer: Optional[str] = Field(default=None, max_length=200)


def build_router(db, require_admin: Callable[..., Awaitable[None]], get_client: Callable[..., Awaitable[dict]],
                 new_access_key: Callable[[], str]) -> APIRouter:
    router = APIRouter()
    admin = [Depends(require_admin)]

    async def find_request(request_id: str) -> dict:
        doc = await db.demo_requests.find_one({"id": request_id}, {"_id": 0})
        if not doc:
            raise HTTPException(status_code=404, detail="Demande introuvable.")
        doc.setdefault("status", "nouveau")
        return doc

    async def new_download_link(owner: dict) -> dict:
        """Un lien de téléchargement neuf pour `owner` ({request_id} ou {client_key})."""
        release = latest_release()
        if release is None:
            raise HTTPException(status_code=503,
                                detail="Aucun installateur n'est disponible pour le moment. Contactez Beaver.")
        token = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(days=link_days())
        await db.downloads.insert_one({
            "token": token, **owner, "file": release.name, "created_at": _now_iso(),
            "expires_at": expires.isoformat(), "count": 0,
        })
        return {"url": f"{site_url()}/api/download/{token}", "version": release_version(release),
                "size": release.stat().st_size, "expires_at": expires.isoformat()}

    # ---- Administration ----
    @router.get("/admin/requests", dependencies=admin)
    async def list_requests(limit: int = 300):
        cursor = db.demo_requests.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        for d in docs:
            d.setdefault("status", "nouveau")
        return docs

    @router.get("/admin/releases", dependencies=admin)
    async def release_info():
        release = latest_release()
        return {
            "licensing_configured": licensing.is_configured(),
            "releases_dir": str(releases_dir()),
            "latest": None if release is None else {
                "file": release.name, "version": release_version(release), "size": release.stat().st_size},
        }

    @router.post("/admin/requests/{request_id}/status", dependencies=admin)
    async def set_status(request_id: str, payload: StatusIn):
        doc = await find_request(request_id)
        if payload.status not in ("commande", "annule", "nouveau"):
            raise HTTPException(status_code=400, detail="Statut modifiable : nouveau, commande ou annule.")
        if doc["status"] == "livre":
            raise HTTPException(status_code=409, detail="Commande déjà livrée.")
        await db.demo_requests.update_one({"id": request_id}, {
            "$set": {"status": payload.status, "updated_at": _now_iso()}, "$unset": {"delivery_error": ""}})
        if payload.status != "commande":
            return {"success": True, "status": payload.status}

        # Commande confirmée : la livraison part toute seule, aux conditions du devis.
        terms = {**DEFAULT_TERMS, **{k: v for k, v in (doc.get("quote") or {}).items() if k in DEFAULT_TERMS}}
        months = terms["licence_months"]
        expires = add_months(date.today(), months) if months else None
        try:
            delivered = await deliver_order({**doc, "status": "commande"}, expires, terms["seats"], None)
        except HTTPException as exc:
            logger.warning("Livraison automatique de %s impossible : %s", request_id, exc.detail)
            await db.demo_requests.update_one({"id": request_id}, {"$set": {"delivery_error": exc.detail}})
            return {"success": True, "status": "commande", "delivered": False, "delivery_error": exc.detail}
        return {**delivered, "delivered": True}

    @router.post("/admin/requests/{request_id}/quote", dependencies=admin)
    async def send_quote(request_id: str, payload: QuoteIn):
        doc = await find_request(request_id)
        if doc["status"] in ("livre", "annule"):
            raise HTTPException(status_code=409, detail="Ce dossier est clos.")
        until = date.today() + timedelta(days=payload.validity_days)
        amount = f"{payload.amount_ht:,.2f}".replace(",", " ").replace(".", ",")
        quote = {"amount_ht": payload.amount_ht, "details": payload.details,
                 "valid_until": until.isoformat(), "sent_at": _now_iso(),
                 "licence_months": payload.licence_months, "seats": payload.seats}
        email_status = await send_customer_email(
            doc["email"],
            f"Votre devis Beaver — {doc['entreprise']}",
            f"Bonjour {doc['nom']},",
            [
                "Merci pour votre intérêt pour Beaver. Voici notre proposition pour "
                f"{doc['entreprise']}.",
                f"Montant : {amount} € HT.",
                f"Licence : {licence_terms(payload.licence_months, payload.seats)}.",
                payload.details,
                f"Ce devis est valable jusqu'au {until:%d/%m/%Y}.",
                "Pour commander, ou pour toute question, répondez simplement à ce mail. Dès "
                "votre commande confirmée, vous recevez par mail le logiciel, sa licence et "
                "l'accès à votre espace client.",
            ],
        )
        quote["email_status"] = email_status
        await db.demo_requests.update_one({"id": request_id}, {"$set": {
            "status": "devis_envoye", "quote": quote, "updated_at": _now_iso()}})
        return {"success": True, "status": "devis_envoye", "email_status": email_status}

    async def send_delivery(doc: dict, licence_key: str, licence_expires: Optional[str],
                            access_key: str, link: dict) -> str:
        validity = ("sans limite de durée" if not licence_expires
                    else f"valable jusqu'au {date.fromisoformat(licence_expires):%d/%m/%Y}")
        return await send_customer_email(
            doc["email"],
            "Votre logiciel Beaver est prêt",
            f"Bonjour {doc['nom']},",
            [
                f"Votre commande est confirmée : voici de quoi installer et activer Beaver chez "
                f"{doc['entreprise']}.",
                "1. Téléchargez l'installateur avec le bouton ci-dessous (lien valable "
                f"{link_days()} jours ; vous pourrez en obtenir un nouveau depuis votre espace client).",
                "2. Lancez BeaverSetup sur le poste de la ligne et suivez les étapes. Aucun droit "
                "d'administrateur n'est nécessaire. Si le poste a une carte graphique NVIDIA, laissez "
                "cochée l'option d'accélération (connexion internet nécessaire pendant l'installation).",
                "3. Au premier lancement, collez la clé de licence ci-dessous dans l'écran d'activation. "
                "Elle se vérifie sans connexion internet.",
                f"Votre licence est {validity}.",
            ],
            code_blocks=[
                ("Clé de licence (à copier en entier)", licence_key),
                ("Clé d'accès à votre espace client", access_key),
            ],
            button=(f"Télécharger Beaver {link['version']}", link["url"]),
            closing=[
                f"Votre espace client ({site_url()}/beta) donne accès aux guides, au "
                "téléchargement de l'installateur et au suivi de vos demandes. À la première "
                "connexion, choisissez « Première connexion » et saisissez la clé d'accès ci-dessus.",
                "Conservez ce mail : la clé de licence vous sera demandée pour réinstaller Beaver.",
            ],
        )

    @router.post("/admin/requests/{request_id}/deliver", dependencies=admin)
    async def deliver(request_id: str, payload: DeliverIn):
        """Livraison à la main : relance après un échec, ou conditions particulières."""
        doc = await find_request(request_id)
        return await deliver_order(doc, payload.licence_expires, payload.seats, payload.customer)

    async def deliver_order(doc: dict, licence_expires: Optional[date], seats: int,
                            customer: Optional[str]) -> dict:
        request_id = doc["id"]
        if doc["status"] == "livre":
            raise HTTPException(status_code=409, detail="Déjà livrée : utilisez « Renvoyer le mail ».")
        if doc["status"] == "annule":
            raise HTTPException(status_code=409, detail="Ce dossier est annulé.")
        try:
            licence = licensing.issue(customer or doc["entreprise"], doc["email"], licence_expires, seats)
        except licensing.LicensingNotConfigured as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        link = await new_download_link({"request_id": request_id})   # 503 sans installateur : rien n'est créé
        access_key = new_access_key()
        await db.beta_keys.insert_one({
            "id": secrets.token_hex(16), "key": access_key, "status": "unused",
            "company": doc["entreprise"], "notes": f"Commande {request_id}",
            "created_at": _now_iso(), "expires_at": None, "used_at": None,
            "request_id": request_id, "licence_id": licence.id, "licence_key": licence.key,
            "licence_expires": licence.expires, "licence_seats": licence.seats,
        })
        record = {"id": licence.id, "key": licence.key, "customer": licence.customer,
                  "email": licence.email, "issued": licence.issued, "expires": licence.expires,
                  "seats": licence.seats, "request_id": request_id, "access_key": access_key,
                  "created_at": _now_iso()}
        await db.licences.insert_one(dict(record))
        email_status = await send_delivery(doc, licence.key, licence.expires, access_key, link)
        await db.demo_requests.update_one({"id": request_id}, {"$unset": {"delivery_error": ""}, "$set": {
            "status": "livre", "updated_at": _now_iso(),
            "delivery": {"licence_id": licence.id, "licence_expires": licence.expires,
                         "seats": licence.seats, "access_key": access_key,
                         "delivered_at": _now_iso(), "email_status": email_status,
                         "version": link["version"]}}})
        return {"success": True, "status": "livre", "licence_id": licence.id, "licence_key": licence.key,
                "access_key": access_key, "download": link, "email_status": email_status}

    @router.post("/admin/requests/{request_id}/resend", dependencies=admin)
    async def resend(request_id: str):
        doc = await find_request(request_id)
        if doc["status"] != "livre":
            raise HTTPException(status_code=409, detail="Ce dossier n'a pas encore été livré.")
        lic = await db.licences.find_one({"request_id": request_id}, {"_id": 0}, sort=[("created_at", -1)])
        if not lic:
            raise HTTPException(status_code=404, detail="Licence introuvable pour ce dossier.")
        link = await new_download_link({"request_id": request_id})
        email_status = await send_delivery(doc, lic["key"], lic.get("expires"), lic["access_key"], link)
        await db.demo_requests.update_one({"id": request_id}, {"$set": {
            "delivery.email_status": email_status, "delivery.resent_at": _now_iso(), "updated_at": _now_iso()}})
        return {"success": True, "email_status": email_status, "download": link}

    @router.get("/admin/licences", dependencies=admin)
    async def list_licences(limit: int = 300):
        cursor = db.licences.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)

    # ---- Espace client ----
    @router.get("/beta/download")
    async def client_download(c: dict = Depends(get_client)):
        return await new_download_link({"client_key": c["key"]})

    @router.get("/beta/licence")
    async def client_licence(c: dict = Depends(get_client)):
        key_doc = await db.beta_keys.find_one({"key": c["key"]}, {"_id": 0})
        if not key_doc or not key_doc.get("licence_key"):
            return {"licence": None}
        return {"licence": {"id": key_doc.get("licence_id"), "key": key_doc["licence_key"],
                            "expires": key_doc.get("licence_expires"), "seats": key_doc.get("licence_seats", 1)}}

    # ---- Téléchargement public (lien reçu par mail) ----
    @router.get("/download/{token}")
    async def download(token: str):
        link = await db.downloads.find_one({"token": token}, {"_id": 0})
        if not link:
            raise HTTPException(status_code=404, detail="Lien de téléchargement inconnu.")
        expires = datetime.fromisoformat(link["expires_at"])
        if datetime.now(timezone.utc) > expires:
            raise HTTPException(status_code=410,
                                detail="Ce lien a expiré : téléchargez Beaver depuis votre espace client.")
        path = releases_dir() / link["file"]
        if not path.is_file():
            path = latest_release()          # the file was replaced by a newer version
        if path is None or not path.is_file():
            raise HTTPException(status_code=503, detail="Installateur indisponible, contactez Beaver.")
        await db.downloads.update_one({"token": token},
                                      {"$inc": {"count": 1}, "$set": {"last_at": _now_iso()}})
        return FileResponse(path, media_type="application/vnd.microsoft.portable-executable",
                            filename=path.name)

    return router
