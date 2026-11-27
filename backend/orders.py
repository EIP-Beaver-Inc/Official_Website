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
- livre : le site émet la licence signée (licensing.py), ouvre l'espace client
  du client et crée un lien de téléchargement de l'installateur, puis envoie le
  tout au client. Une seule clé : la licence (BVR1....) active le logiciel et
  connecte aussi à l'espace client.
  Si la livraison automatique échoue (pas d'installateur publié, clé de
  signature absente), le dossier reste « commande » avec la raison, et le
  bouton « Livrer » la relance.

Les installateurs sont déposés dans RELEASES_DIR : BeaverSetup-<version>.exe
pour Windows, BeaverSetup-<version>-linux.run pour Linux. Le plus récent de
chaque est servi ; la livraison envoie un lien pour chaque système disponible.
Un lien de téléchargement est valable DOWNLOAD_LINK_DAYS jours (30 par défaut) ;
l'espace client en recrée un à la demande.
"""
from __future__ import annotations

import logging
import os
import re
import secrets
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

import licensing
from mailer import send_customer_email

logger = logging.getLogger("beaver.orders")

STATUSES = ["nouveau", "devis_envoye", "commande", "livre", "annule"]
# Les installateurs servis, par système : le nom que leur donnent
# Beaver/installer/build-installer.ps1 et build-installer.sh.
INSTALLERS = {
    "windows": re.compile(r"^BeaverSetup-(\d+)\.(\d+)\.(\d+)\.exe$"),
    "linux": re.compile(r"^BeaverSetup-(\d+)\.(\d+)\.(\d+)-linux\.run$"),
}
PLATFORM_NAMES = {"windows": "Windows", "linux": "Linux"}
MEDIA_TYPES = {"windows": "application/vnd.microsoft.portable-executable", "linux": "application/x-sh"}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def site_url() -> str:
    return os.environ.get("SITE_URL", "https://beaver-website.fr").rstrip("/")


def releases_dir() -> Path:
    return Path(os.environ.get("RELEASES_DIR", "/releases"))


def link_days() -> int:
    try:
        return max(1, int(os.environ.get("DOWNLOAD_LINK_DAYS", "30")))
    except ValueError:
        return 30


def latest_release(platform: str = "windows") -> Path | None:
    """L'installateur de plus haute version pour ce système, ou None."""
    folder = releases_dir()
    if not folder.is_dir():
        return None
    found = []
    for f in folder.iterdir():
        m = INSTALLERS[platform].match(f.name)
        if m and f.is_file():
            found.append((tuple(int(x) for x in m.groups()), f))
    return max(found)[1] if found else None


def platform_of(name: str) -> str | None:
    return next((p for p, pattern in INSTALLERS.items() if pattern.match(name)), None)


def release_version(path: Path) -> str:
    platform = platform_of(path.name)
    return ".".join(INSTALLERS[platform].match(path.name).groups()) if platform else ""


def release_info(path: Path | None) -> dict | None:
    return None if path is None else {
        "file": path.name, "version": release_version(path), "size": path.stat().st_size}


# ====================== Modèles ======================
class QuoteIn(BaseModel):
    amount_ht: float = Field(gt=0, le=1_000_000)
    details: str = Field(min_length=1, max_length=4000)
    validity_days: int = Field(default=30, ge=1, le=365)
    # Ce que la livraison émettra : durée de la licence en mois (None : sans
    # limite), à compter de la livraison, et nombre de postes.
    licence_months: int | None = Field(default=12, ge=1, le=120)
    seats: int = Field(default=1, ge=1, le=100)

    @field_validator("amount_ht", mode="before")
    @classmethod
    def _amount_as_typed(cls, value):
        """« 4 500,50 € » tel que saisi : espaces, symbole et virgule acceptés."""
        if isinstance(value, str):
            cleaned = re.sub(r"[\s\u00a0\u202f€]|HT", "", value, flags=re.IGNORECASE).replace(",", ".")
            try:
                return float(cleaned)
            except ValueError:
                return value
        return value


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


def licence_terms(months: int | None, seats: int) -> str:
    duration = "sans limite de durée" if not months else (
        f"{months // 12} an{'s' if months >= 24 else ''}" if months % 12 == 0 else f"{months} mois")
    return f"{duration}, {seats} poste{'s' if seats > 1 else ''}"


class StatusIn(BaseModel):
    status: str


class DeliverIn(BaseModel):
    # None : licence sans limite de durée.
    licence_expires: date | None = None
    seats: int = Field(default=1, ge=1, le=100)
    # Nom inscrit dans la licence (affiché par le logiciel) ; par défaut l'entreprise.
    customer: str | None = Field(default=None, max_length=200)


def build_router(db, require_admin: Callable[..., Awaitable[None]],
                 get_client: Callable[..., Awaitable[dict]]) -> APIRouter:
    router = APIRouter()
    admin = [Depends(require_admin)]

    async def find_request(request_id: str) -> dict:
        doc = await db.demo_requests.find_one({"id": request_id}, {"_id": 0})
        if not doc:
            raise HTTPException(status_code=404, detail="Demande introuvable.")
        doc.setdefault("status", "nouveau")
        return doc

    async def new_download_link(owner: dict, platform: str = "windows") -> dict:
        """Un lien de téléchargement neuf pour `owner` ({request_id} ou {client_key})."""
        release = latest_release(platform)
        if release is None:
            raise HTTPException(status_code=503, detail=(
                f"Aucun installateur {PLATFORM_NAMES[platform]} n'est disponible pour le moment. "
                "Contactez Beaver."))
        token = secrets.token_urlsafe(32)
        expires = datetime.now(UTC) + timedelta(days=link_days())
        await db.downloads.insert_one({
            "token": token, **owner, "file": release.name, "platform": platform, "created_at": _now_iso(),
            "expires_at": expires.isoformat(), "count": 0,
        })
        return {"url": f"{site_url()}/api/download/{token}", "version": release_version(release),
                "platform": platform, "file": release.name,
                "size": release.stat().st_size, "expires_at": expires.isoformat()}

    async def new_download_links(owner: dict) -> dict[str, dict]:
        """Un lien par système dont l'installateur est publié (Windows d'abord)."""
        available = [p for p in INSTALLERS if latest_release(p) is not None]
        if not available:
            raise HTTPException(status_code=503,
                                detail="Aucun installateur n'est disponible pour le moment. Contactez Beaver.")
        return {p: await new_download_link(owner, p) for p in available}

    # ---- Administration ----
    @router.get("/admin/requests", dependencies=admin)
    async def list_requests(limit: int = 300):
        cursor = db.demo_requests.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        for d in docs:
            d.setdefault("status", "nouveau")
        return docs

    @router.get("/admin/releases", dependencies=admin)
    async def releases():
        installers = {p: release_info(latest_release(p)) for p in INSTALLERS}
        return {
            "licensing_configured": licensing.is_configured(),
            "releases_dir": str(releases_dir()),
            # Le plus récent de tous : ce que la livraison annonce.
            "latest": installers["windows"] or installers["linux"],
            "installers": installers,
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
                ("Merci pour votre intérêt pour Beaver. Voici notre proposition pour "
                f"{doc['entreprise']}."),
                f"Montant : {amount} € HT.",
                f"Licence : {licence_terms(payload.licence_months, payload.seats)}.",
                payload.details,
                f"Ce devis est valable jusqu'au {until:%d/%m/%Y}.",
                ("Pour commander, ou pour toute question, répondez simplement à ce mail. Dès "
                "votre commande confirmée, vous recevez par mail le logiciel, sa licence et "
                "l'accès à votre espace client."),
            ],
        )
        quote["email_status"] = email_status
        await db.demo_requests.update_one({"id": request_id}, {"$set": {
            "status": "devis_envoye", "quote": quote, "updated_at": _now_iso()}})
        return {"success": True, "status": "devis_envoye", "email_status": email_status}

    async def send_delivery(doc: dict, licence_key: str, licence_expires: str | None, links: dict[str, dict],
                            access_key: str | None = None) -> str:
        """`access_key` : seulement pour une commande livrée avant la clé unique,
        dont l'espace client s'ouvre encore avec son ancienne clé d'accès."""
        validity = ("sans limite de durée" if not licence_expires
                    else f"valable jusqu'au {date.fromisoformat(licence_expires):%d/%m/%Y}")
        available = " ou ".join(PLATFORM_NAMES[p] for p in links)
        steps = []
        if "windows" in links:
            steps.append("2. Windows : lancez BeaverSetup et suivez les étapes. Aucun droit d'administrateur "
                         "n'est nécessaire. Si le poste a une carte graphique NVIDIA, laissez cochée l'option "
                         "d'accélération (connexion internet nécessaire pendant l'installation).")
        if "linux" in links:
            steps.append(f"{'3' if 'windows' in links else '2'}. Linux (Ubuntu 22.04 ou plus récent, 64 bits) : "
                         f"ouvrez un terminal dans le dossier du téléchargement et tapez « bash "
                         f"{links['linux']['file']} ». Beaver s'installe pour votre compte, sans mot de passe "
                         "administrateur, avec son icône dans le menu des applications.")
        return await send_customer_email(
            doc["email"],
            "Votre logiciel Beaver est prêt",
            f"Bonjour {doc['nom']},",
            [
                (f"Votre commande est confirmée : voici de quoi installer et activer Beaver chez "
                f"{doc['entreprise']}."),
                (f"1. Téléchargez l'installateur du système du poste de la ligne ({available}) avec "
                f"le bouton ci-dessous (lien valable {link_days()} jours ; vous pourrez en obtenir un "
                "nouveau depuis votre espace client)."),
                *steps,
                (f"{len(steps) + 2}. Au premier lancement, collez votre clé de licence ci-dessous (le texte "
                "qui commence par BVR1.) dans l'écran d'activation. Elle se vérifie sans connexion internet."),
                f"Votre licence est {validity}.",
            ],
            code_blocks=[("Votre clé de licence (à copier en entier)", licence_key)]
            + ([("Clé d'accès à votre espace client", access_key)]
               if access_key and access_key != licence_key else []),
            buttons=[(f"Télécharger pour {PLATFORM_NAMES[p]} ({link['version']})", link["url"])
                     for p, link in links.items()],
            closing=[
                (f"La même clé vous connecte à votre espace client ({site_url()}/beta) : guides, "
                "téléchargement de l'installateur et suivi de vos demandes."),
                "Conservez ce mail : votre clé de licence vous sera demandée pour réinstaller Beaver.",
            ],
        )

    @router.post("/admin/requests/{request_id}/deliver", dependencies=admin)
    async def deliver(request_id: str, payload: DeliverIn):
        """Livraison à la main : relance après un échec, ou conditions particulières."""
        doc = await find_request(request_id)
        return await deliver_order(doc, payload.licence_expires, payload.seats, payload.customer)

    async def deliver_order(doc: dict, licence_expires: date | None, seats: int,
                            customer: str | None) -> dict:
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

        links = await new_download_links({"request_id": request_id})   # 503 sans installateur : rien n'est créé
        link = next(iter(links.values()))
        # L'espace client, ouvert d'office avec ce que la commande dit du client :
        # la licence est sa clé de connexion, sans « première connexion » à faire.
        access_key = licence.key
        await db.beta_keys.insert_one({
            "id": secrets.token_hex(16), "key": access_key, "status": "active",
            "company": doc["entreprise"], "notes": f"Commande {request_id}",
            "created_at": _now_iso(), "expires_at": None, "used_at": _now_iso(),
            "request_id": request_id, "licence_id": licence.id, "licence_key": licence.key,
            "licence_expires": licence.expires, "licence_seats": licence.seats,
        })
        await db.beta_clients.insert_one({
            "id": str(uuid.uuid4()), "key": access_key, "company": doc["entreprise"],
            "contact_name": doc["nom"], "email": doc["email"], "phone": doc.get("telephone"),
            "registered_at": _now_iso(), "session_token": str(uuid.uuid4()),
        })
        record = {"id": licence.id, "key": licence.key, "customer": licence.customer,
                  "email": licence.email, "issued": licence.issued, "expires": licence.expires,
                  "seats": licence.seats, "request_id": request_id, "access_key": access_key,
                  "created_at": _now_iso()}
        await db.licences.insert_one(dict(record))
        email_status = await send_delivery(doc, licence.key, licence.expires, links)
        await db.demo_requests.update_one({"id": request_id}, {"$unset": {"delivery_error": ""}, "$set": {
            "status": "livre", "updated_at": _now_iso(),
            "delivery": {"licence_id": licence.id, "licence_expires": licence.expires,
                         "seats": licence.seats, "access_key": access_key,
                         "delivered_at": _now_iso(), "email_status": email_status,
                         "version": link["version"], "platforms": list(links)}}})
        return {"success": True, "status": "livre", "licence_id": licence.id, "licence_key": licence.key,
                "access_key": access_key, "download": link, "downloads": links, "email_status": email_status}

    @router.post("/admin/requests/{request_id}/resend", dependencies=admin)
    async def resend(request_id: str):
        doc = await find_request(request_id)
        if doc["status"] != "livre":
            raise HTTPException(status_code=409, detail="Ce dossier n'a pas encore été livré.")
        lic = await db.licences.find_one({"request_id": request_id}, {"_id": 0}, sort=[("created_at", -1)])
        if not lic:
            raise HTTPException(status_code=404, detail="Licence introuvable pour ce dossier.")
        links = await new_download_links({"request_id": request_id})
        email_status = await send_delivery(doc, lic["key"], lic.get("expires"), links, lic.get("access_key"))
        await db.demo_requests.update_one({"id": request_id}, {"$set": {
            "delivery.email_status": email_status, "delivery.resent_at": _now_iso(), "updated_at": _now_iso()}})
        return {"success": True, "email_status": email_status, "download": next(iter(links.values())),
                "downloads": links}

    @router.get("/admin/licences", dependencies=admin)
    async def list_licences(limit: int = 300):
        cursor = db.licences.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)

    # ---- Espace client ----
    @router.get("/beta/download")
    async def client_download(platform: str = "windows", c: dict = Depends(get_client)):  # noqa: B008 - usage FastAPI ; Annotated ne voit pas get_client (local) avec les annotations différées
        if platform not in INSTALLERS:
            raise HTTPException(status_code=400, detail="Système attendu : windows ou linux.")
        return await new_download_link({"client_key": c["key"]}, platform)

    @router.get("/beta/licence")
    async def client_licence(c: dict = Depends(get_client)):  # noqa: B008 - usage FastAPI ; Annotated ne voit pas get_client (local) avec les annotations différées
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
        if datetime.now(UTC) > expires:
            raise HTTPException(status_code=410,
                                detail="Ce lien a expiré : téléchargez Beaver depuis votre espace client.")
        platform = link.get("platform") or platform_of(link["file"]) or "windows"
        path = releases_dir() / link["file"]
        if not path.is_file():
            path = latest_release(platform)  # the file was replaced by a newer version
        if path is None or not path.is_file():
            raise HTTPException(status_code=503, detail="Installateur indisponible, contactez Beaver.")
        await db.downloads.update_one({"token": token},
                                      {"$inc": {"count": 1}, "$set": {"last_at": _now_iso()}})
        return FileResponse(path, media_type=MEDIA_TYPES[platform], filename=path.name)

    return router
